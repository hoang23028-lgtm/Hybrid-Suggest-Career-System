

from __future__ import annotations

import argparse
import hashlib
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))

from kbs.metrics_db import (
    MetricsRow,
    alert_if_degraded,
    connect,
    insert_metrics,
    log_alert,
    new_run_id,
)
from kbs.config import get_model_path

from scripts import create_data, train_model
from scripts.evaluate_model import evaluate_block


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

try:  # Windows terminals can default to a non-UTF8 codepage
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _sha256_file(path: Path) -> str | None:
    if not path.exists():
        return None
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _try_git_sha(repo_dir: Path) -> str | None:
    try:
        import subprocess

        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=str(repo_dir),
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        return out or None
    except Exception:
        return None


def run_pipeline(
    *,
    blocks: list[str],
    eval_max_samples: int | None,
    skip_data: bool,
    skip_train: bool,
    skip_eval: bool,
    extract_rules: bool,
    rules_top_k_total: int,
    rules_top_k_per_class: int,
    rules_min_conf: float,
    rules_min_samples: int,
    out_dir: str,
):
    run_id = new_run_id("retrain")
    timestamp = _utc_now_iso()
    repo_dir = Path(__file__).parent.parent
    rules_path = repo_dir / "rules_config.json"
    rules_sha256 = _sha256_file(rules_path)
    code_git_sha = _try_git_sha(repo_dir)

    logger.info("=" * 80)
    logger.info("RETRAIN PIPELINE v3 (data -> train -> eval -> metrics_db)")
    logger.info("=" * 80)
    logger.info(f"run_id={run_id}")
    logger.info(f"blocks={blocks} eval_max_samples={eval_max_samples}")

    if not skip_data:
        logger.info("\n[1/4] create_data")
        create_data.main()
    else:
        logger.info("\n[1/4] create_data (skipped)")

    train_summaries: dict[str, dict] = {}
    if not skip_train:
        logger.info("\n[2/4] train_model")
        for b in blocks:
            _, train_metrics = train_model.train_model(b)
            train_summaries[b] = train_metrics
    else:
        logger.info("\n[2/4] train_model (skipped)")

    eval_summaries: dict[str, dict] = {}
    if not skip_eval:
        logger.info("\n[3/4] evaluate_model")
        for b in blocks:
            eval_summaries[b] = evaluate_block(b, max_samples=eval_max_samples)
    else:
        logger.info("\n[3/4] evaluate_model (skipped)")

    logger.info("\n[4/4] persist metrics to model_metrics.db")
    con = connect()
    try:
        for b in blocks:
            if b in eval_summaries:
                ml = eval_summaries[b]["ml"]
                hy = eval_summaries[b]["hybrid"]

                common_details = {
                    "phase": "eval",
                    "code_git_sha": code_git_sha,
                    "rules_sha256": rules_sha256,
                    "labels": eval_summaries[b].get("labels"),
                    "label_names": eval_summaries[b].get("label_names"),
                }

                # model path is repo-relative in config (e.g. models/rf_model_khtn.pkl)
                model_path = repo_dir / get_model_path(b)
                if model_path.exists():
                    common_details["model"] = {
                        "path": str(model_path),
                        "sha256": _sha256_file(model_path),
                        "size_bytes": model_path.stat().st_size,
                        "mtime": datetime.fromtimestamp(model_path.stat().st_mtime, tz=timezone.utc)
                        .replace(microsecond=0)
                        .isoformat(),
                    }
                insert_metrics(
                    con,
                    MetricsRow(
                        block=b,
                        system="ml",
                        accuracy=ml["accuracy"],
                        precision=ml["precision"],
                        recall=ml["recall"],
                        f1=ml["f1"],
                        num_samples=eval_summaries[b]["num_test"],
                        run_id=run_id,
                        timestamp=timestamp,
                        details={
                            **common_details,
                            "system_details": {
                                "num_hybrid_eval": eval_summaries[b]["num_hybrid_eval"],
                                "confusion_matrix": ml.get("confusion_matrix"),
                                "classification_report": ml.get("report"),
                            },
                        },
                    ),
                )
                insert_metrics(
                    con,
                    MetricsRow(
                        block=b,
                        system="hybrid",
                        accuracy=hy["accuracy"],
                        precision=hy["precision"],
                        recall=hy["recall"],
                        f1=hy["f1"],
                        num_samples=eval_summaries[b]["num_hybrid_eval"],
                        run_id=run_id,
                        timestamp=timestamp,
                        details={
                            **common_details,
                            "system_details": {
                                "avg_hybrid_score": hy.get("avg_hybrid_score"),
                                "confusion_matrix": hy.get("confusion_matrix"),
                                "classification_report": hy.get("report"),
                            },
                        },
                    ),
                )

                if hy["accuracy"] + 1e-12 < ml["accuracy"]:
                    log_alert(
                        con,
                        level="warning",
                        block=b,
                        message=f"Hybrid accuracy lower than ML ({hy['accuracy']:.4f} < {ml['accuracy']:.4f})",
                    )

                # Baseline degradation alerts (rolling mean of last N runs)
                alert_if_degraded(con, block=b, system="ml", new_accuracy=float(ml["accuracy"]))
                alert_if_degraded(con, block=b, system="hybrid", new_accuracy=float(hy["accuracy"]))
            else:
                # If evaluation skipped, still store train summary (if present)
                if b in train_summaries and "test_accuracy" in train_summaries[b]:
                    insert_metrics(
                        con,
                        MetricsRow(
                            block=b,
                            system="ml",
                            accuracy=train_summaries[b].get("test_accuracy", 0.0),
                            precision=0.0,
                            recall=0.0,
                            f1=0.0,
                            num_samples=train_summaries[b].get("num_test", 0),
                            run_id=run_id,
                            timestamp=timestamp,
                            details={
                                "phase": "train_only",
                                "code_git_sha": code_git_sha,
                                "rules_sha256": rules_sha256,
                                **train_summaries[b],
                            },
                        ),
                    )
    finally:
        con.close()

    if extract_rules:
        logger.info("\n[extra] rule extraction")
        import subprocess
        import sys

        out_path = Path(out_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        for b in blocks:
            cmd = [
                sys.executable,
                str(Path(__file__).parent / "rule_extraction.py"),
                "--block",
                b,
                "--out-dir",
                out_dir,
                "--min-confidence",
                str(rules_min_conf),
                "--min-samples",
                str(rules_min_samples),
                "--top-k-total",
                str(rules_top_k_total),
                "--top-k-per-class",
                str(rules_top_k_per_class),
            ]
            logger.info(" ".join(cmd))
            subprocess.check_call(cmd)

    logger.info("\nDONE.")
    logger.info(f"- run_id: {run_id}")
    logger.info("- metrics stored in: model_metrics.db (table: metrics)")
    if extract_rules:
        logger.info(f"- extracted rules in: {out_dir}/")


def main():
    parser = argparse.ArgumentParser(description="Retrain pipeline v3 (step 7).")
    parser.add_argument("--blocks", nargs="+", default=["khtn", "khxh"], choices=["khtn", "khxh"])
    parser.add_argument("--eval-max-samples", type=int, default=0, help="Giới hạn số mẫu khi eval hybrid (0=all)")
    parser.add_argument("--skip-data", action="store_true")
    parser.add_argument("--skip-train", action="store_true")
    parser.add_argument("--skip-eval", action="store_true")

    parser.add_argument("--extract-rules", action="store_true", help="Chạy rule_extraction sau pipeline")
    parser.add_argument("--rules-top-k-total", type=int, default=50)
    parser.add_argument("--rules-top-k-per-class", type=int, default=10)
    parser.add_argument("--rules-min-confidence", type=float, default=0.6)
    parser.add_argument("--rules-min-samples", type=int, default=50)
    parser.add_argument("--rules-out-dir", default="extracted_rules")

    args = parser.parse_args()
    eval_max = args.eval_max_samples if args.eval_max_samples and args.eval_max_samples > 0 else None

    run_pipeline(
        blocks=args.blocks,
        eval_max_samples=eval_max,
        skip_data=args.skip_data,
        skip_train=args.skip_train,
        skip_eval=args.skip_eval,
        extract_rules=args.extract_rules,
        rules_top_k_total=args.rules_top_k_total,
        rules_top_k_per_class=args.rules_top_k_per_class,
        rules_min_conf=args.rules_min_confidence,
        rules_min_samples=args.rules_min_samples,
        out_dir=args.rules_out_dir,
    )


if __name__ == "__main__":
    main()


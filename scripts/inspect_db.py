import sqlite3
from pathlib import Path
import sys


def main():
    repo_root = Path(__file__).parent.parent
    sys.path.insert(0, str(repo_root))
    db_path = Path(__file__).parent.parent / "model_metrics.db"
    print(f"db_path={db_path} exists={db_path.exists()} size={db_path.stat().st_size if db_path.exists() else None}")
    if not db_path.exists():
        return

    con = sqlite3.connect(str(db_path))
    cur = con.cursor()
    cur.execute("SELECT name, type FROM sqlite_master WHERE type IN ('table','view') ORDER BY type,name")
    print("\nobjects:")
    for name, typ in cur.fetchall():
        print(f"  {typ}: {name}")

    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [r[0] for r in cur.fetchall()]

    for t in tables:
        print(f"\n-- {t}")
        cur.execute(f"PRAGMA table_info({t})")
        for row in cur.fetchall():
            print(" ", row)

    con.close()


if __name__ == "__main__":
    main()


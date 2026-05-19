"""Tests cột nganh_hoc theo khối."""

import pandas as pd
import pytest

from kbs.config import MAJOR_NAMES, get_features, get_majors
from kbs.knowledge_rules import KnowledgeRuleEngine
from kbs.label_assignment import assign_major_labels, mask_complete_block


def _major_index_from_name(name: str) -> int:
    return MAJOR_NAMES.index(name)


@pytest.mark.parametrize(
    "block,scores",
    [
        ("khtn", [9, 5, 7, 8.5, 5, 4]),
        ("khtn", [6, 7, 6, 5, 8, 8.5]),
        ("khxh", [6, 7.5, 7, 8.5, 6, 8.5]),
        ("khxh", [5, 8, 8.5, 6, 8, 6]),
    ],
)
def test_predict_major_index_matches_ranking(block, scores):
    engine = KnowledgeRuleEngine(block=block)
    pred = engine.predict_major_index(scores)
    top_name = engine.get_ranking(scores)[0]["major"]
    assert pred in get_majors(block)
    assert pred == _major_index_from_name(top_name)


def test_mask_complete_block():
    row_khtn = {
        "toan": 8,
        "van": 7,
        "anh": 7,
        "ly": 6,
        "hoa": 6,
        "sinh": 6,
        "lich_su": None,
        "dia_ly": None,
        "gdcd": None,
    }
    row_khxh = {
        "toan": 8,
        "van": 7,
        "anh": 7,
        "ly": None,
        "hoa": None,
        "sinh": None,
        "lich_su": 7,
        "dia_ly": 7,
        "gdcd": 7,
    }
    df = pd.DataFrame([row_khtn, row_khxh])
    assert mask_complete_block(df, "khtn").tolist() == [True, False]
    assert mask_complete_block(df, "khxh").tolist() == [False, True]


def test_assign_major_labels_column():
    engine = KnowledgeRuleEngine(block="khtn")
    scores = [9, 5, 7, 8.5, 5, 4]
    df = pd.DataFrame([scores], columns=get_features("khtn"))
    labels = assign_major_labels(df, "khtn", log_every=0)
    assert labels.iloc[0] == engine.predict_major_index(scores)

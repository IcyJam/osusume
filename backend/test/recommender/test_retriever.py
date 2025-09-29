import pytest
from datetime import datetime
from typing import Optional, List

from qdrant_client.http.models import Filter, FieldCondition, Range, MatchValue, DatetimeRange

from app.recommender.retriever import build_filter_from_constraints


# --- Minimal mock models for testing ---
class ScoreRange:
    def __init__(self, min: Optional[float], max: Optional[float]):
        self.min = min
        self.max = max

class TypeConstraint:
    def __init__(self, included_types: List, excluded_types: List):
        self.included_types = included_types
        self.excluded_types = excluded_types

class DateRange:
    def __init__(self, start: Optional[datetime], end: Optional[datetime]):
        self.start = start
        self.end = end

class StatusConstraint:
    def __init__(self, included_statuses: List, excluded_statuses: List):
        self.included_statuses = included_statuses
        self.excluded_statuses = excluded_statuses

class DummyEnum:
    def __init__(self, value):
        self.value = value

class RecommenderQueryHardConstraints:
    def __init__(self, score_range, type, date_range, status):
        self.score_range = score_range
        self.type = type
        self.date_range = date_range
        self.status = status

# --- Tests ---

def test_returns_none_when_no_constraints():
    constraints = RecommenderQueryHardConstraints(
        ScoreRange(None, None),
        TypeConstraint([], []),
        DateRange(None, None),
        StatusConstraint([], [])
    )
    assert build_filter_from_constraints(constraints) is None

def test_score_range_only():
    constraints = RecommenderQueryHardConstraints(
        ScoreRange(5.0, 9.0),
        TypeConstraint([], []),
        DateRange(None, None),
        StatusConstraint([], [])
    )
    f = build_filter_from_constraints(constraints)
    assert isinstance(f, Filter)
    assert any(fc.key == "score" for fc in f.must)
    fc = next(fc for fc in f.must if fc.key == "score")
    assert fc.range.gte == 5.0
    assert fc.range.lte == 9.0

def test_type_include_and_exclude():
    constraints = RecommenderQueryHardConstraints(
        ScoreRange(None, None),
        TypeConstraint([DummyEnum("anime"), DummyEnum("manga")], [DummyEnum("novel")]),
        DateRange(None, None),
        StatusConstraint([], [])
    )
    f = build_filter_from_constraints(constraints)
    include_keys = [fc.key for fc in f.should]
    exclude_keys = [fc.key for fc in f.must_not]
    assert "type" in include_keys
    assert "type" in exclude_keys
    assert any(isinstance(fc.match, MatchValue) and fc.match.value == "anime" for fc in f.should)

def test_date_range_only():
    start = datetime(2020, 1, 1)
    end = datetime(2021, 1, 1)
    constraints = RecommenderQueryHardConstraints(
        ScoreRange(None, None),
        TypeConstraint([], []),
        DateRange(start, end),
        StatusConstraint([], [])
    )
    f = build_filter_from_constraints(constraints)
    fc = next(fc for fc in f.must if fc.key == "start_date")
    assert isinstance(fc.range, DatetimeRange)
    assert fc.range.gte == datetime(2020, 1, 1)
    assert fc.range.lte == datetime(2021, 1, 1)

def test_status_include_and_exclude():
    constraints = RecommenderQueryHardConstraints(
        ScoreRange(None, None),
        TypeConstraint([], []),
        DateRange(None, None),
        StatusConstraint([DummyEnum("completed")], [DummyEnum("dropped")])
    )
    f = build_filter_from_constraints(constraints)
    assert any(fc.key == "status" and fc.match.value == "completed" for fc in f.should)
    assert any(fc.key == "status" and fc.match.value == "dropped" for fc in f.must_not)

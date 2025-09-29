import pytest
from datetime import datetime
from app.recommender.query_processor import (
    parse_score_range,
    parse_type_constraints,
    parse_date_range,
    parse_status_constraints,
    parse_hard_constraints,
    process_query,
    ScoreRange,
    DateRange,
    MediaType,
    Status,
    ProcessedRecommenderQuery,
)


# --- Fixtures for sample data ---

@pytest.fixture
def raw_query_dict():
    return {
        "embedding_text": "An anime with action and adventure",
        "keywords": ["action", "adventure"],
        "hard_constraints": {
            "score_range": {"min": 7.5, "max": 9.2},
            "type": {"include": ["TV", "MOVIE"], "exclude": ["MANGA"]},
            "date_range": {"start": "2020-01", "end": "2021-12"},
            "status": {"include": ["FINISHED"], "exclude": ["ONGOING"]},
        },
    }


# --- Unit tests for converter functions ---

@pytest.mark.parametrize("data,expected_min,expected_max", [
    ({"min": 7.0, "max": 9.5}, 7.0, 9.5),
    ({"min": None, "max": 8.0}, None, 8.0),
    ({"min": 5.0, "max": None}, 5.0, None),
])
def test_parse_score_range(data, expected_min, expected_max):
    result = parse_score_range(data)
    assert isinstance(result, ScoreRange)
    assert result.min == expected_min
    assert result.max == expected_max


@pytest.mark.parametrize("data,included,excluded", [
    ({"include": ["TV"], "exclude": []}, [MediaType.TV], []),
    ({"include": ["MOVIE", "OVA"], "exclude": ["MANGA"]},
     [MediaType.MOVIE, MediaType.OVA], [MediaType.MANGA]),
])
def test_parse_type_constraints(data, included, excluded):
    result = parse_type_constraints(data)
    assert result.included_types == included
    assert result.excluded_types == excluded


@pytest.mark.parametrize("data,expected_start,expected_end", [
    ({"start": "2020-01", "end": "2021-06"},
     datetime(2020, 1, 1), datetime(2021, 6, 1)),
    ({"start": "2019-12", "end": None},
     datetime(2019, 12, 1), None),
    ({"start": None, "end": None}, None, None),
])
def test_parse_date_range(data, expected_start, expected_end):
    result = parse_date_range(data)
    assert isinstance(result, DateRange)
    assert result.start == expected_start
    assert result.end == expected_end


@pytest.mark.parametrize("data,included,excluded", [
    ({"include": ["FINISHED"], "exclude": []},
     [Status.FINISHED], []),
    ({"include": ["ONGOING"], "exclude": ["ONGOING"]},
     [Status.ONGOING], [Status.ONGOING]),
])
def test_parse_status_constraints(data, included, excluded):
    result = parse_status_constraints(data)
    assert result.included_statuses == included
    assert result.excluded_statuses == excluded


# --- Integration test for process_query ---

def test_process_query_integration(monkeypatch, raw_query_dict):
    # Mock get_processed_query to return our fixture
    monkeypatch.setattr("app.recommender.query_processor.get_processed_recommender_query", lambda _, __: raw_query_dict)

    result = process_query("any user input", prompt_id="123")
    assert isinstance(result, ProcessedRecommenderQuery)
    assert result.embedding_text == "An anime with action and adventure"
    assert "action" in result.keywords
    assert result.hard_constraints.score_range.min == 7.5
    assert result.hard_constraints.type.included_types[0] == MediaType.TV
    assert result.hard_constraints.date_range.start == datetime(2020, 1, 1)
    assert result.hard_constraints.status.included_statuses[0] == Status.FINISHED

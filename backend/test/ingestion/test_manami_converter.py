from datetime import date

import pytest
from app.ingestion.converters.manami_converter import (
    convert_date,
    convert_status,
    convert_external_url,
    convert_media_entry, convert_type, convert_score
)


# ----------- convert_type -----------

@pytest.mark.parametrize("input_enum,expected", [
    ("TV", "TV"),
    ("MOVIE", "MOVIE"),
    ("OVA", "OVA"),
    ("ONA", "ONA"),
    ("SPECIAL", "SPECIAL"),
    ("OTHER", "OTHER"),
    ("UNKNOWN", "OTHER"),
    (None, "OTHER"),
])
def test_convert_type(input_enum, expected):
    assert convert_type(input_enum) == expected


# ----------- convert_date -----------

@pytest.mark.parametrize("input_dict,expected", [
    ({"season": "SPRING", "year": 2023}, date(2023, 4, 1)),
    ({"season": "SUMMER", "year": 2021}, date(2021, 7, 1)),
    ({"season": "FALL", "year": 2022}, date(2022, 10, 1)),
    ({"season": "WINTER", "year": 2020}, date(2020, 1, 1)),
    ({"year": 2023}, date(2023, 1, 1)),  # No season given
    ({}, None),
    (None, None),
])
def test_convert_date(input_dict, expected):
    assert convert_date(input_dict) == expected


# ----------- convert_status -----------

@pytest.mark.parametrize("input_status,expected", [
    ("FINISHED", "FINISHED"),
    ("ONGOING", "ONGOING"),
    ("UPCOMING", "UPCOMING"),
    ("UNKNOWN", "UNKNOWN"),
    ("CANCELLED", None),
    ("", None),
    (None, None),
])
def test_convert_status(input_status, expected):
    assert convert_status(input_status) == expected


# ----------- convert_external_url -----------

def test_convert_external_url_priority_match():
    urls = [
        "https://example.com",
        "https://anidb.net/anime/1234",
        "https://myanimelist.net/anime/5678"
    ]
    result = convert_external_url(urls)
    assert result == "https://myanimelist.net/anime/5678"


def test_convert_external_url_fallback():
    urls = ["https://unknownsite.org/anime/123"]
    result = convert_external_url(urls)
    assert result == "https://unknownsite.org/anime/123"


def test_convert_external_url_empty_list():
    assert convert_external_url([]) is None


def test_convert_external_url_malformed_url():
    urls = ["not_a_url", "https://anilist.co/anime/9999"]
    assert convert_external_url(urls) == "https://anilist.co/anime/9999"


# -------------- convert_score --------------
@pytest.mark.parametrize("input_dict,expected", [
    ({"arithmeticGeometricMean": 6.310,
      "arithmeticMean": 6.313,
      "median": 6.374
      }, 6.374),
    ({}, None),
    ({"bad_key": 10.0}, None),
    ({"median": 10}, 10.0),
    (None, None),
])
def test_convert_score(input_dict, expected):
    assert convert_score(input_dict) == expected


# ----------- convert_media_entry -----------

def test_convert_media_entry_basic():
    entry = {
        "title": "Naruto",
        "type": "TV",
        "animeSeason": {"season": "FALL", "year": 2002},
        "sources": ["https://anilist.co/anime/20"],
        "picture": "https://img.com/naruto.jpg",
        "status": "FINISHED",
        "tags": ["shounen", "ninja"],
        "score":{"median": 8.30, "mean":8.00},
    }

    result = convert_media_entry(entry)
    assert result["title"] == "Naruto"
    assert result["type"] == "TV"
    assert result["start_date"] == date(2002, 10, 1)
    assert result["status"] == "FINISHED"
    assert result["external_url"] == "https://anilist.co/anime/20"
    assert result["image_url"] == "https://img.com/naruto.jpg"
    assert result["content_descriptors"] == ["shounen", "ninja"]
    assert result["score"] == 8.30
    assert result["summary"] is None
    assert result["end_date"] is None

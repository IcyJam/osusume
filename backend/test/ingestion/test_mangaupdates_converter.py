# tests/test_converters.py
import pytest
from datetime import date

from app.ingestion.converters.mangaupdates_converter import convert_type, convert_date, convert_image, convert_status, \
    convert_content_descriptors, convert_media_entry


# ----------- convert_type -----------
@pytest.mark.parametrize(
    "raw, expected",
    [
        ("Artbook", "ARTBOOK"),
        ("Doujinshi", "DOUJINSHI"),
        ("Manga", "MANGA"),
        ("Novel", "NOVEL"),
        ("Manhwa", "MANHWA"),
        ("Manhua", "MANHWA"),  # alias → MANHWA
        ("Unknown", "OTHER"),
        (None, "OTHER"),
    ],
)
def test_convert_type(raw, expected):
    assert convert_type(raw) == expected


# ----------- convert_date -----------

def test_convert_date_valid():
    assert convert_date("2021") == date(2021, 1, 1)


@pytest.mark.parametrize("bad", ["", "abcd", None])
def test_convert_date_invalid(bad):
    assert convert_date(bad) is None


# ----------- convert_image -----------

def test_convert_image_ok():
    img_dict = {"url": {"original": "https://img/original.png"}}
    assert convert_image(img_dict) == "https://img/original.png"


@pytest.mark.parametrize("bad", [None, {}, {"url": {}}, {"url": None}])
def test_convert_image_missing(bad):
    assert convert_image(bad) is None


# ----------- convert_status -----------

@pytest.mark.parametrize(
    "completed,status,expected",
    [
        (True, "Ongoing", "FINISHED"),
        (False, "Complete", "FINISHED"),
        (False, "Ongoing", "ONGOING"),
        (False, "Hiatus", "SUSPENDED"),
        (False, "Cancelled", "CANCELLED"),
        (False, "Something else", None),
    ],
)
def test_convert_status(completed, status, expected):
    assert convert_status(completed, status) == expected


# ----------- convert_content_descriptors -----------

def test_convert_content_descriptors():
    genres = [{"genre": "Action"}, {"genre": None}]
    cats = [{"category": "Martial Arts"}, {"genre": "Comedy"}]  # wrong object to test fallback
    result = convert_content_descriptors(genres, cats)
    assert sorted(result) == ["Action", "Martial Arts"]


# -------------- convert_media_entry --------------

def test_convert_media_entry_full():
    entry = {
        "type": "Manga",
        "title": "Example",
        "description": "Lorem ipsum",
        "year": "1999",
        "url": "https://site/series/123",
        "image": {"url": {"original": "img.png"}},
        "completed": False,
        "status": "Ongoing",
        "bayesian_rating": 7.8,
        "genres": [{"genre": "Action"}],
        "categories": [{"category": "Adventure"}],
    }
    converted = convert_media_entry(entry)
    assert converted["type"] == "MANGA"
    assert converted["title"] == "Example"
    assert converted["start_date"] == date(1999, 1, 1)
    assert converted["image_url"] == "img.png"
    assert converted["status"] == "ONGOING"
    assert sorted(converted["content_descriptors"]) == ["Action", "Adventure"]

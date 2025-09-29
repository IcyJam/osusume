from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.models import Base, Media, ContentDescriptor, MediaType, Status
from app.ingestion.loaders.media_loader import (
    sanitize_name,
    get_or_create_content_descriptor,
    create_new_media,
    update_existing_media,
    load_all_media, get_or_create_content_descriptor_cached
)


# ----------- Fixture: Temporary In-Memory DB -----------

@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    session_local = sessionmaker(bind=engine)
    with session_local() as session:
        yield session


# ----------- sanitize_name -----------

@pytest.mark.parametrize("name,expected", [
    ("  Action ", "action"),
    ("Slice of Life", "slice of life"),
    ("Romance", "romance"),
    ("", ""),
])
def test_sanitize_name(name, expected):
    assert sanitize_name(name) == expected


# ----------- get_or_create_content_descriptor -----------

def test_get_or_create_content_descriptor_creates_new(session):
    cd = get_or_create_content_descriptor(session, "Psychological")
    assert cd.content_descriptor == "psychological"
    assert session.query(ContentDescriptor).count() == 1


def test_get_or_create_content_descriptor_reuses_existing(session):
    first = get_or_create_content_descriptor(session, "Drama")
    second = get_or_create_content_descriptor(session, "  drama  ")
    assert first.content_descriptor_id == second.content_descriptor_id
    assert session.query(ContentDescriptor).count() == 1


def test_get_or_create_content_descriptor_cached_creates_new(session):
    cd = get_or_create_content_descriptor_cached(session, "Psychological", cache={})
    assert cd.content_descriptor == "psychological"
    assert session.query(ContentDescriptor).count() == 1


def test_get_or_create_content_descriptor_cached_reuses_existing(session):
    cache = {}
    first = get_or_create_content_descriptor_cached(session, "Drama", cache=cache)
    second = get_or_create_content_descriptor(session, "  drama  ", cache={"drama": first})
    assert first.content_descriptor_id == second.content_descriptor_id
    assert session.query(ContentDescriptor).count() == 1


# ----------- upsert_media -----------

def test_create_new_media():
    data = {
        "title": "Naruto",
        "type": "TV",
        "summary": "Naruto Uzumaki wants to become Hokage.",
        "start_date": date(2002, 10, 3),
        "end_date": date(2007, 2, 8),
        "external_url": "https://anilist.co/anime/20",
        "image_url": "https://img.com/naruto.jpg",
        "status": "finished",
        "score": 8.30,
        "content_descriptors": ["shounen"]
    }

    descriptors = [ContentDescriptor(content_descriptor="shounen")]
    media_type = MediaType.TV
    status = Status.FINISHED

    media = create_new_media(data, media_type, status, descriptors)

    assert media.start_date == date(2002, 10, 3)
    assert media.end_date == date(2007, 2, 8)
    assert media.external_url == "https://anilist.co/anime/20"
    assert media.image_url == "https://img.com/naruto.jpg"
    assert media.score == 8.30
    assert media.status == Status.FINISHED


def test_update_existing_media():
    # First insert
    data1 = {
        "title": "Naruto",
        "type": "TV",
        "summary": None,
        "start_date": date(2002, 10, 1),
        "end_date": None,
        "external_url": "https://anilist.co/anime/20",
        "image_url": "https://img.com/naruto.jpg",
        "status": "FINISHED",
        "score": 8.30,
        "content_descriptors": ["shounen"]
    }

    descriptors1 = [ContentDescriptor(content_descriptor="shounen")]
    media_type = MediaType.TV
    status = Status.FINISHED

    media = create_new_media(data1, media_type, status, descriptors1)

    # Update with different descriptor
    data2 = data1.copy()
    data2["content_descriptors"] = ["action"]
    descriptors2 = [ContentDescriptor(content_descriptor="action")]

    update_existing_media(media, data2, media_type, status, descriptors2)

    assert len(media.content_descriptors) == 1
    assert media.content_descriptors[0].content_descriptor == "action"


# ----------- load_all_media -----------

def test_load_all_media_bulk_insert(session):
    entries = [
        {
            "title": "Death Note",
            "type": "TV",
            "summary": None,
            "start_date": date(2006, 10, 1),
            "end_date": None,
            "external_url": "https://anilist.co/anime/1535",
            "image_url": "https://img.com/deathnote.jpg",
            "status": "FINISHED",
            "score": 8.30,
            "content_descriptors": ["psychological", "supernatural"]
        },
        {
            "title": "Bleach",
            "type": "TV",
            "summary": None,
            "start_date": date(2004, 10, 1),
            "end_date": None,
            "external_url": "https://anilist.co/anime/269",
            "image_url": "https://img.com/bleach.jpg",
            "status": "FINISHED",
            "score": 8.30,
            "content_descriptors": ["action", "shounen"]
        }
    ]

    load_all_media(session, entries)

    assert session.query(Media).count() == 2
    assert session.query(ContentDescriptor).count() == 4


def test_load_all_media_bulk_insert_with_updates(session):
    initial_entries = [
        {
            "title": "Death Note",
            "type": "TV",
            "summary": None,
            "start_date": date(2006, 10, 1),
            "end_date": None,
            "external_url": "https://anilist.co/anime/1535",
            "image_url": "https://img.com/deathnote.jpg",
            "status": "FINISHED",
            "score": 8.30,
            "content_descriptors": ["psychological", "supernatural"]
        },
        {
            "title": "Bleach",
            "type": "TV",
            "summary": None,
            "start_date": date(2004, 10, 1),
            "end_date": None,
            "external_url": "https://anilist.co/anime/269",
            "image_url": "https://img.com/bleach.jpg",
            "status": "FINISHED",
            "content_descriptors": ["action", "shounen"]
        },
        {
            "title": "Bleach",
            "type": "OVA",
            "summary": None,
            "start_date": date(2004, 10, 1),
            "end_date": None,
            "external_url": "https://anilist.co/anime/270",
            "image_url": "https://img.com/bleach.jpg",
            "status": "FINISHED",
            "score": 8.30,
            "content_descriptors": ["action", "shounen"]
        },
        {
            "title": "Bleach",
            "type": "OVA",
            "summary": None,
            "start_date": date(2004, 10, 1),
            "end_date": None,
            "external_url": "https://other_url/bleach",
            "image_url": "https://img.com/bleach.jpg",
            "status": "FINISHED",
            "score": 8.30,
            "content_descriptors": ["action", "shounen"]
        }
    ]

    updated_entries = [
        {
            "title": "Bleach",
            "type": "TV",
            "summary": None,
            "start_date": date(2004, 10, 1),
            "end_date": None,
            "external_url": "https://anilist.co/anime/269",
            "image_url": "https://img.com/bleach.jpg",
            "status": "FINISHED",
            "score": 8.30,
            "content_descriptors": ["action"]
        }
    ]

    load_all_media(session, initial_entries)
    load_all_media(session, updated_entries)

    media = session.query(Media).filter_by(title="Bleach", type="TV").first()

    assert session.query(Media).count() == 4
    assert session.query(ContentDescriptor).count() == 4
    assert len(media.content_descriptors) == 1

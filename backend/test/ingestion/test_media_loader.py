import pytest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.models import Base, Media, ContentDescriptor, MediaType, Status
from ingestion.loaders.media_loader import (
    sanitize_name,
    get_or_create_content_descriptor,
    upsert_media,
    load_all_media
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


# ----------- upsert_media -----------

def test_upsert_media_creates_new(session):
    data = {
        "title": "Naruto",
        "type": "anime",
        "summary": "Naruto Uzumaki wants to become Hokage.",
        "start_date": date(2002, 10, 3),
        "end_date": date(2007, 2, 8),
        "external_url": "https://anilist.co/anime/20",
        "image_url": "https://img.com/naruto.jpg",
        "status": "finished",
        "content_descriptors": ["shounen", "ninja"]
    }

    media = upsert_media(session, data)
    session.commit()

    db_media = session.query(Media).filter_by(title="Naruto").first()
    assert db_media is not None
    assert db_media.title == "Naruto"
    assert db_media.type == MediaType.anime
    assert db_media.summary == "Naruto Uzumaki wants to become Hokage."
    assert media.start_date == date(2002, 10, 3)
    assert media.end_date == date(2007, 2, 8)
    assert media.external_url == "https://anilist.co/anime/20"
    assert media.image_url == "https://img.com/naruto.jpg"
    assert media.status == Status.finished
    assert session.query(ContentDescriptor).count() == 2


def test_upsert_media_updates_existing(session):
    # First insert
    data1 = {
        "title": "Naruto",
        "type": "anime",
        "summary": None,
        "start_date": date(2002, 10, 1),
        "end_date": None,
        "external_url": "https://anilist.co/anime/20",
        "image_url": "https://img.com/naruto.jpg",
        "status": "finished",
        "content_descriptors": ["shounen"]
    }

    upsert_media(session, data1)
    session.commit()

    # Update with different descriptor
    data2 = data1.copy()
    data2["content_descriptors"] = ["action"]

    upsert_media(session, data2)
    session.commit()

    media = session.query(Media).filter_by(title="Naruto").first()
    assert media is not None
    assert len(media.content_descriptors) == 1
    assert media.content_descriptors[0].content_descriptor == "action"
    assert session.query(ContentDescriptor).count() == 2


# ----------- load_all_media -----------

def test_load_all_media_bulk_insert(session):
    entries = [
        {
            "title": "Death Note",
            "type": "anime",
            "summary": None,
            "start_date": date(2006, 10, 1),
            "end_date": None,
            "external_url": "https://anilist.co/anime/1535",
            "image_url": "https://img.com/deathnote.jpg",
            "status": "finished",
            "content_descriptors": ["psychological", "supernatural"]
        },
        {
            "title": "Bleach",
            "type": "anime",
            "summary": None,
            "start_date": date(2004, 10, 1),
            "end_date": None,
            "external_url": "https://anilist.co/anime/269",
            "image_url": "https://img.com/bleach.jpg",
            "status": "finished",
            "content_descriptors": ["action", "shounen"]
        }
    ]

    load_all_media(session, entries)

    assert session.query(Media).count() == 2
    assert session.query(ContentDescriptor).count() == 4

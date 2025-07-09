from datetime import datetime, UTC

from app.db.models import Media, ContentDescriptor, MediaType, Status
from sqlalchemy.orm import Session
from tqdm import tqdm


def sanitize_name(name: str) -> str:
    return name.strip().lower()


def preload_content_descriptors(session: Session) -> dict[str, ContentDescriptor]:
    descriptors = session.query(ContentDescriptor).all()
    return {sanitize_name(d.content_descriptor): d for d in descriptors}


def preload_media(session: Session) -> dict[tuple[str, MediaType, str], Media]:
    media_entries = session.query(Media).all()
    return {(m.title, m.type, m.external_url): m for m in media_entries}

def get_or_create_content_descriptor(
        session: Session,
        name: str,
        cache: dict[str, ContentDescriptor] = None
) -> ContentDescriptor:
    if cache is None: cache = {}

    key = sanitize_name(name)
    if key in cache:
        return cache[key]

    descriptor = session.query(ContentDescriptor).filter_by(content_descriptor=key).first()
    if descriptor is None:
        descriptor = ContentDescriptor(content_descriptor=key)
        session.add(descriptor)
        session.flush()

    cache[key] = descriptor
    return descriptor


def get_or_create_content_descriptor_cached(
        session: Session,
        name: str,
        cache: dict[str, ContentDescriptor]
) -> ContentDescriptor:
    # Unlike get_or_create_content_descriptor, this function does not have a database fallback if the cache is out of sync.
    # It should only be used when the cache is explicitly and rigorously managed.

    key = sanitize_name(name)
    if key in cache:
        return cache[key]

    descriptor = ContentDescriptor(content_descriptor=key)
    session.add(descriptor)
    session.flush()

    cache[key] = descriptor
    return descriptor


def create_new_media(entry, media_type, status, descriptors):
    media = Media(
        title=entry["title"],
        type=media_type,
        summary=entry.get("summary"),
        start_date=entry.get("start_date"),
        end_date=entry.get("end_date"),
        external_url=entry.get("external_url"),
        image_url=entry.get("image_url"),
        score=entry.get("score"),
        status=status,
    )
    media.content_descriptors = descriptors
    return media


def update_existing_media(existing_media, new_entry, media_type, status, descriptors):
    existing_media.type = media_type
    existing_media.summary = new_entry.get("summary")
    existing_media.start_date = new_entry.get("start_date")
    existing_media.end_date = new_entry.get("end_date")
    existing_media.external_url = new_entry.get("external_url")
    existing_media.image_url = new_entry.get("image_url")
    existing_media.score = new_entry.get("score")
    existing_media.status = status
    existing_media.updated_at = datetime.now(UTC)
    existing_media.content_descriptors = descriptors


def load_all_media(session: Session, entries: list[dict]):
    media_cache = preload_media(session)
    content_descriptors_cache = preload_content_descriptors(session)
    for entry in tqdm(entries, desc="Loading media"):
        title = entry.get("title")
        type_str = entry.get("type")
        external_url = entry.get("external_url")
        media_type = MediaType(type_str) if type_str else None
        media_key = (title, media_type, external_url)
        media = media_cache.get(media_key)

        status = Status(entry["status"]) if entry["status"] else None
        descriptors = [
            get_or_create_content_descriptor_cached(session=session, name=d, cache=content_descriptors_cache)
            for d in entry.get("content_descriptors", [])
        ]

        if media:
            update_existing_media(media, entry, media_type, status, descriptors)
        else:
            media = create_new_media(entry, media_type, status, descriptors)
            session.add(media)
            media_cache[media_key] = media

    session.flush()
    session.commit()

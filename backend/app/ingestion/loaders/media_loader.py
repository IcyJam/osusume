from db.models import Media, ContentDescriptor, MediaType, Status
from sqlalchemy.orm import Session
from datetime import datetime, UTC
from tqdm import tqdm


def sanitize_name(name: str) -> str:
    return name.strip().lower()


def get_or_create_content_descriptor(session: Session, name: str) -> ContentDescriptor:
    name = sanitize_name(name)
    content_descriptor = session.query(ContentDescriptor).filter_by(content_descriptor=name).first()
    if not content_descriptor:
        content_descriptor = ContentDescriptor(content_descriptor=name)
        session.add(content_descriptor)
        session.flush() # flush needed to get content_descriptor_id, used to fill in the association table
    return content_descriptor


def upsert_media(session: Session, media_data: dict) -> Media:
    media = session.query(Media).filter_by(title=media_data["title"]).first()

    media_type = MediaType(media_data["type"]) if media_data["type"] else None
    status = Status(media_data["status"]) if media_data["status"] else None

    descriptors = [
        get_or_create_content_descriptor(session, d)
        for d in media_data.get("content_descriptors", [])
    ]

    if media:
        # Update existing
        media.type = media_type
        media.summary = media_data.get("summary")
        media.start_date = media_data.get("start_date")
        media.end_date = media_data.get("end_date")
        media.external_url = media_data.get("external_url")
        media.image_url = media_data.get("image_url")
        media.status = status
        media.updated_at = datetime.now(UTC)
        media.content_descriptors = descriptors
    else:
        # Create new
        media = Media(
            title=media_data["title"],
            type=media_type,
            summary=media_data.get("summary"),
            start_date=media_data.get("start_date"),
            end_date=media_data.get("end_date"),
            external_url=media_data.get("external_url"),
            image_url=media_data.get("image_url"),
            status=status,
        )
        media.content_descriptors = descriptors
        session.add(media)

    return media


def load_all_media(session: Session, entries: list[dict]):
    for entry in tqdm(entries, desc="Loading media"):
        upsert_media(session, entry)
    session.commit()

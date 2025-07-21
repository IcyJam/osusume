# Integration tests, prefixed with underscore to not be run automatically with pytest
from sqlalchemy import func
from sqlalchemy.orm import selectinload

from app.db.database import SessionLocal
from app.db.models import Media, ContentDescriptor
from app.vector_db.initialize_vdb import initialize_media, initialize_content_descriptors
from app.vector_db.vector_database import vector_database_client


def test_initialize_media():
    test_collection = "media_initialization_test"
    max_media = 100

    vector_database_client.delete_collection(test_collection)

    with SessionLocal() as session:
        media_sample = (
            session.query(Media)
            .options(selectinload(Media.content_descriptors))
            .order_by(func.random())
            .limit(max_media)
            .all()
        )

    initialize_media(
        media_list=media_sample,
        vdb_client=vector_database_client,
        collection_name=test_collection
    )

def test_initialize_content_descriptors():
    test_collection = "cd_initialization_test"
    max_cd = 100

    vector_database_client.delete_collection(test_collection)

    with SessionLocal() as session:
        cd_sample = (
            session.query(ContentDescriptor)
            .options(selectinload(ContentDescriptor.media))
            .order_by(func.random())
            .limit(max_cd)
            .all()
        )

    initialize_content_descriptors(
        cd_list=cd_sample,
        vdb_client=vector_database_client,
        collection_name=test_collection
    )


if __name__ == "__main__":
    # test_initialize_media()
    test_initialize_content_descriptors()
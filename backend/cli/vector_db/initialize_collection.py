import typer

from app.db.database import SessionLocal
from app.vector_db.initialize_vdb import initialize_all_media, initialize_all_content_descriptors
from app.vector_db.vector_database import vector_database_client, DEFAULT_MEDIA_COLLECTION_NAME, \
    DEFAULT_CD_COLLECTION_NAME

app = typer.Typer()


@app.command()
def media(
        collection_name: str = typer.Option(default=DEFAULT_MEDIA_COLLECTION_NAME),
        batch_size: int = typer.Option(default=1000, ),
):
    """Embed all media in database to initialize vector database collection."""
    with SessionLocal() as db_client:
        initialize_all_media(db_client, vector_database_client, collection_name=collection_name, batch_size=batch_size)


@app.command()
def content_descriptors(collection_name: str = typer.Option(default=DEFAULT_CD_COLLECTION_NAME)):
    """Embed all content descriptors in database to initialize vector database collection."""
    with SessionLocal() as db_client:
        initialize_all_content_descriptors(db_client, vector_database_client, collection_name)

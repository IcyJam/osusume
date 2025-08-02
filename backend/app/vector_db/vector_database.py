from qdrant_client import QdrantClient

DEFAULT_MEDIA_COLLECTION_NAME = "media"
DEFAULT_CD_COLLECTION_NAME = "content_descriptors"

vector_database_client = QdrantClient(host="qdrant", port=6333)

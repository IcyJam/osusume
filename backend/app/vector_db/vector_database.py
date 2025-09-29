from typing import Optional, List

from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter, ScoredPoint

DEFAULT_MEDIA_COLLECTION_NAME = "media"
DEFAULT_CD_COLLECTION_NAME = "content_descriptors"

vector_database_client = QdrantClient(host="qdrant", port=6333)

def get_top_k_from_media(vector, k, vdb_filter: Optional[Filter]=None) -> List[ScoredPoint]:
    """ Returns the k closest points from the given vector in the media collection. """

    response = vector_database_client.query_points(
        collection_name=DEFAULT_MEDIA_COLLECTION_NAME,
        query=vector,
        limit=k,
        query_filter=vdb_filter
    )

    return response.points
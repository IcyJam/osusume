from typing import List

from qdrant_client.http.models import ScoredPoint


def rerank(points: List[ScoredPoint], n_selected: int) -> List[int]:
    print("Re-ranking vectors...")
    """ Return the media_id for the top n_selected recommendations. """
    return [point.id for point in points[:n_selected]]

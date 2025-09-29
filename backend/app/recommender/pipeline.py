from typing import List

from app.db.models import Media
from app.recommender.embedder import embed_processed_query
from app.recommender.query_processor import process_query
from app.recommender.reranker import rerank
from app.recommender.retriever import retrieve_top_k, retrieve_media
from common.config.recommender.recommender_config import RecommenderConfiguration


def get_recommendations(user_query:str, cfg:RecommenderConfiguration) -> List[Media]:
    """
    Get media recommendations for a user query.
    :param user_query: User recommendation query.
    :param cfg: Recommender configuration.
    :return: A list of Media objects from the database.
    """
    processed_query     = process_query(user_query=user_query, prompt_id=cfg.prompt_id)
    embedded_query      = embed_processed_query(model=cfg.embedder, dimensions=cfg.dimensions, query=processed_query)
    k_closest_points    = retrieve_top_k(embedded_query=embedded_query, processed_query=processed_query, k=cfg.top_k)
    selected_media_ids  = rerank(points=k_closest_points, n_selected=cfg.n_selected)
    selected_media      = retrieve_media(media_ids=selected_media_ids)
    return selected_media

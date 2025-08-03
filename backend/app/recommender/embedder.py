from app.recommender.models import ProcessedRecommenderQuery, EmbeddedRecommenderQuery
from app.services.openai_service import get_embedding


def embed_processed_query(model:str, dimensions:int, query: ProcessedRecommenderQuery) -> EmbeddedRecommenderQuery:
    """ Embed a processed query. """
    print(f"Embedding query...")
    sorted_keywords = sorted(query.keywords)
    combined_text = query.embedding_text + ", " + ", ".join(sorted_keywords)
    embedding = get_embedding(
        text=combined_text,
        model=model,
        dimensions=dimensions,
    )

    return EmbeddedRecommenderQuery(
        vector=embedding,
    )

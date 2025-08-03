import json
import os
from typing import List

from qdrant_client.models import Distance, VectorParams, PointStruct
from sqlalchemy.orm import selectinload
from tqdm import tqdm

from app.db.models import Media, ContentDescriptor
from app.services.openai_service import get_embeddings

import re
import string

from app.vector_db.vector_database import DEFAULT_MEDIA_COLLECTION_NAME, DEFAULT_CD_COLLECTION_NAME
from common.config.recommender.recommender_config import RecommenderConfiguration, get_recommender_config

RECOVERY_FILE = "qdrant_processed_media_ids.json"


def sanitize_text(text: str | None) -> str:
    if not text or not isinstance(text, str):
        return ""

    text = text.lower().strip()  # Lowercase and strip leading/trailing whitespace
    text = "".join(ch for ch in text if ch in string.printable)  # Remove non-printable/control characters
    text = re.sub(r"\s+", " ", text)  # Collapse multiple whitespace characters into one space
    text = re.sub(r"[^a-z0-9\s.,;:!?'-]", "", text)  # keep only alphanumerics and basic punctuation

    return text


def initialize_all_media(
        db_client, vdb_client,
        collection_name=DEFAULT_MEDIA_COLLECTION_NAME,
        batch_size=1000,
        config: RecommenderConfiguration = None,
):
    if config is None:
        config = get_recommender_config()

    all_media: List[Media] = (
        db_client
        .query(Media)
        .options(selectinload(Media.content_descriptors))
        .all()
    )
    return initialize_media(
        all_media,
        vdb_client,
        collection_name=collection_name,
        batch_size=batch_size,
        config=config
    )


def initialize_media(
        media_list,
        vdb_client,
        collection_name=DEFAULT_MEDIA_COLLECTION_NAME,
        batch_size=1000,
        config: RecommenderConfiguration = None
):
    if config is None:
        config = get_recommender_config()

    # Create collection in VDB
    vdb_client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=config.dimensions,
            distance=Distance.COSINE,
        )
    )

    # Load already processed IDs for recovery
    if os.path.exists(RECOVERY_FILE):
        with open(RECOVERY_FILE, "r") as f:
            processed_ids = set(json.load(f))
    else:
        processed_ids = set()

    media_list = [m for m in media_list if m.media_id not in processed_ids]

    for i in tqdm(range(0, len(media_list), batch_size), desc="Initializing media"):
        batch = media_list[i:i + batch_size]
        media_data_to_embed = []
        valid_media = []

        # Embed media in batch
        for media in batch:
            # Process string
            sanitized_summary = sanitize_text(media.summary)
            sorted_tags = sorted(cd.content_descriptor for cd in media.content_descriptors)
            combined_text = sanitized_summary + ", " + ", ".join(sorted_tags) if sanitized_summary \
                else ", ".join(sorted_tags)

            # Add media to the list of valid media to process if the text to embed is not empty
            if combined_text.strip():
                media_data_to_embed.append(combined_text)
                valid_media.append(media)

        if not valid_media:
            continue

        try:
            vectors = get_embeddings(
                texts=media_data_to_embed,
                model=config.embedder,
                dimensions=config.dimensions,
            )
        except Exception as e:
            print(f"Embedding failed for batch {i // batch_size}: {e}")
            continue

        media_points = [
            PointStruct(
                id=media.media_id,
                vector=vectors[idx],
                payload={
                    "title": media.title,
                    "score": media.score,
                    "type": media.type,
                    "start_date": media.start_date,
                    "status": media.status,
                    "content_descriptors": [tag.content_descriptor for tag in media.content_descriptors],
                }
            )
            for idx, media in enumerate(valid_media)
        ]

        try:
            vdb_client.upsert(collection_name=collection_name, points=media_points)
        except Exception as e:
            print(f"Upsert failed for batch {i // batch_size}: {e}")
            continue

        # Save progress
        processed_ids.update(m.media_id for m in valid_media)
        with open(RECOVERY_FILE, "w") as f:
            json.dump(list(processed_ids), f)


def initialize_all_content_descriptors(
        db_client,
        vdb_client,
        collection_name=DEFAULT_CD_COLLECTION_NAME,
        config=None,
):
    if config is None:
        config = get_recommender_config()

    all_cd: List[ContentDescriptor] = (
        db_client
        .query(ContentDescriptor).all()
        .options(selectinload(ContentDescriptor.media))
    )
    initialize_content_descriptors(all_cd, vdb_client, collection_name, config)


def initialize_content_descriptors(
        cd_list,
        vdb_client,
        collection_name=DEFAULT_CD_COLLECTION_NAME,
        config=None,
):
    if config is None:
        config = get_recommender_config()

    vdb_client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=config.dimensions,
            distance=Distance.COSINE,
        )
    )

    cd_data_to_embed = [cd.content_descriptor for cd in cd_list]

    vectors = get_embeddings(
        texts=cd_data_to_embed,
        model=config.embedder,
        dimensions=config.dimensions,
    )

    cd_points = [
        PointStruct(
            id=cd.content_descriptor_id,
            vector=vectors[idx],
            payload={
                "content_descriptor": cd.content_descriptor,
                "usage_count": len(cd.media)
            }
        )
        for idx, cd in enumerate(cd_list)
    ]

    vdb_client.upsert(collection_name=collection_name, points=cd_points)

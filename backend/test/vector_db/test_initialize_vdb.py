import os
from dataclasses import field
from unittest.mock import MagicMock, patch

import pytest
from pydantic.dataclasses import dataclass
from qdrant_client.models import VectorParams, Distance

from app.vector_db.initialize_vdb import initialize_media, initialize_content_descriptors, RECOVERY_FILE
from common.config.recommender.recommender_config import RecommenderConfiguration


@dataclass
class MockDescriptor:
    content_descriptor_id: int
    content_descriptor: str
    media: list = field(default_factory=list)  # cannot set list directly because it is a mutable type


@dataclass
class FakeMedia:
    media_id: int
    title: str
    summary: str
    score: float
    type: str
    start_date: str
    status: str
    content_descriptors: list[MockDescriptor]


@pytest.fixture
def fake_media_entries():
    return [
        FakeMedia(
            media_id=1,
            title="My Hero Academia",
            summary="Heroes///",
            score=8.5,
            type="TV",
            start_date="2016-04-03",
            status="Finished",
            content_descriptors=[
                MockDescriptor(content_descriptor="action", content_descriptor_id=1),
                MockDescriptor(content_descriptor="school", content_descriptor_id=2)
            ],
        ),
        FakeMedia(
            media_id=2,
            title="Violet Evergarden",
            summary="Sad ",
            score=9.0,
            type="TV",
            start_date="2018-01-11",
            status="Finished",
            content_descriptors=[
                MockDescriptor(content_descriptor="drama", content_descriptor_id=3),
                MockDescriptor(content_descriptor="war", content_descriptor_id=4)
            ],
        ),
    ]


@pytest.fixture
def fake_content_descriptors():
    return [
        MockDescriptor(content_descriptor="action", content_descriptor_id=1, media=["Bleach", "Jojo"]),
        MockDescriptor(content_descriptor="drama", content_descriptor_id=3, media=["Naruto"]),
    ]


@pytest.fixture
def mock_config():
    return RecommenderConfiguration(
        embedder="embedder_model",
        dimensions=123,
        prompt_id="123abc",
        top_k=10,
        n_selected=5,
    )


@patch("app.vector_db.initialize_vdb.get_embeddings")  # Patch where it's imported, not where it's defined
def test_initialize_media(mock_get_embeddings, fake_media_entries, mock_config):
    try:
        # Setup
        vdb_client = MagicMock()

        mock_get_embeddings.return_value = [
            [0.1] * 123,
            [0.2] * 123,
        ]

        # Call
        initialize_media(fake_media_entries, vdb_client, collection_name="test_media", config=mock_config)

        # Assertions
        vdb_client.create_collection.assert_called_once_with(
            collection_name="test_media",
            vectors_config=VectorParams(
                size=123,
                distance=Distance.COSINE,
            ),
        )

        mock_get_embeddings.assert_called_once_with(
            texts=[
                "heroes, action, school",
                "sad, drama, war"
            ],
            model="embedder_model",
            dimensions=123,
        )

        # Capture the points
        uploaded_points = vdb_client.upsert.call_args.kwargs["points"]

        assert len(uploaded_points) == 2
        assert uploaded_points[0].id == 1
        assert uploaded_points[0].payload["title"] == "My Hero Academia"
        assert uploaded_points[1].vector == [0.2] * 123
    finally:
        if os.path.exists(RECOVERY_FILE):
            os.remove(RECOVERY_FILE)


@patch("app.vector_db.initialize_vdb.get_embeddings")
def test_initialize_content_descriptors(mock_get_embeddings, fake_content_descriptors, mock_config):
    # Setup
    vdb_client = MagicMock()

    mock_get_embeddings.return_value = [
        [0.1] * 123,
        [0.2] * 123,
    ]

    # Call
    initialize_content_descriptors(fake_content_descriptors, vdb_client, collection_name="test_cd", config=mock_config)

    # Assertions
    vdb_client.create_collection.assert_called_once_with(
        collection_name="test_cd",
        vectors_config=VectorParams(
            size=123,
            distance=Distance.COSINE,
        ),
    )

    mock_get_embeddings.assert_called_once_with(
        texts=["action", "drama"],
        model="embedder_model",
        dimensions=123,
    )

    uploaded_points = vdb_client.upsert.call_args.kwargs["points"]

    assert len(uploaded_points) == 2
    assert uploaded_points[0].id == 1
    assert uploaded_points[0].payload["content_descriptor"] == "action"
    assert uploaded_points[0].payload["usage_count"] == 2
    assert uploaded_points[1].vector == [0.2] * 123

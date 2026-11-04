"""Qdrant storage tests.

* Tests without a marker use Qdrant's in-memory local mode (no server needed).
* Tests marked `integration` use a real Qdrant server at QDRANT_URL (default http://localhost:6333)
  and are skipped automatically if the server is not reachable.
  Start it with: docker compose up -d qdrant
"""

import os
import uuid

import numpy as np
import pytest
from qdrant_client import QdrantClient

from config.settings import Settings
from tactiq.indexing.chunking import Chunk
from tactiq.indexing.metadata import make_document_id
from tactiq.indexing.pipeline import run_indexing_pipeline
from tactiq.indexing.vector_store import QdrantStore

DIMENSION = 8


def make_chunks(source_path, count):
    document_id = make_document_id(source_path)
    return [
        Chunk(
            chunk_id=str(uuid.uuid5(uuid.NAMESPACE_URL, f"{source_path}:{i}")),
            document_id=document_id,
            text=f"chunk {i} of {source_path}",
            metadata={"source": source_path, "source_path": source_path, "file_type": "txt",
                      "page": None, "topic": "low_block", "chunk_index": i, "token_count": 4},
        )
        for i in range(count)
    ]


def random_vectors(count):
    return np.random.default_rng(0).random((count, DIMENSION)).astype(np.float32)


def check_store_behaviour(store):
    """Collection creation, dimension, insertion, payload, idempotency and stale-chunk removal."""
    assert store.ensure_collection(DIMENSION) is True       # created
    assert store.ensure_collection(DIMENSION) is False      # already exists
    assert store.get_vector_dimension() == DIMENSION

    chunks = make_chunks("low_block.txt", 3)
    assert store.upsert_chunks(chunks, random_vectors(3), "test-model") == 3
    assert store.count() == 3

    # Re-ingesting the same document must not create duplicates.
    store.upsert_chunks(chunks, random_vectors(3), "test-model")
    assert store.count() == 3

    # A second document is added next to the first.
    store.upsert_chunks(make_chunks("high_press.txt", 2), random_vectors(2), "test-model")
    assert store.count() == 5

    # If a document shrinks, its old extra chunks are removed.
    store.upsert_chunks(chunks[:1], random_vectors(1), "test-model")
    assert store.count() == 3

    point = store.client.retrieve(store.collection_name, ids=[chunks[0].chunk_id], with_payload=True)[0]
    assert point.payload["chunk_text"] == "chunk 0 of low_block.txt"
    assert point.payload["document_id"] == make_document_id("low_block.txt")
    assert point.payload["source"] == "low_block.txt"
    assert point.payload["embedding_model"] == "test-model"
    assert point.payload["match_id"] is None

    with pytest.raises(ValueError):
        store.ensure_collection(DIMENSION + 1)               # wrong dimension is refused
    with pytest.raises(ValueError):
        store.upsert_chunks(chunks, random_vectors(2), "test-model")  # count mismatch


def test_qdrant_store_in_memory():
    check_store_behaviour(QdrantStore(QdrantClient(":memory:"), "test_collection"))


# ---------------------------------------------------------------------------
# Real Qdrant server
# ---------------------------------------------------------------------------

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")


@pytest.fixture
def server_client():
    client = QdrantClient(url=QDRANT_URL, timeout=5)
    try:
        client.get_collections()
    except Exception as error:
        pytest.skip(f"Qdrant server not reachable at {QDRANT_URL}: {error}")
    yield client
    client.close()


@pytest.fixture
def temporary_collection(server_client):
    name = f"tactiq_test_{uuid.uuid4().hex[:8]}"
    yield name
    if server_client.collection_exists(name):
        server_client.delete_collection(name)


@pytest.mark.integration
def test_qdrant_store_on_server(server_client, temporary_collection):
    check_store_behaviour(QdrantStore(server_client, temporary_collection))


@pytest.mark.integration
@pytest.mark.slow
def test_full_pipeline_on_sample_docs_is_idempotent(server_client, temporary_collection, embedding_model, tmp_path):
    from config.settings import PROJECT_ROOT

    settings = Settings(processed_data_dir=tmp_path, qdrant_collection=temporary_collection)
    store = QdrantStore(server_client, temporary_collection)
    sample_dir = PROJECT_ROOT / "data" / "sample_docs"

    first = run_indexing_pipeline(settings, data_dir=sample_dir, qdrant_store=store, embedding_model=embedding_model)
    second = run_indexing_pipeline(settings, data_dir=sample_dir, qdrant_store=store, embedding_model=embedding_model)

    assert first.failed_files == {}
    assert first.loaded_files == 5
    assert first.chunks_created > 0
    assert first.vectors_stored == first.chunks_created
    assert first.collection_total_points == first.chunks_created
    assert store.get_vector_dimension() == embedding_model.dimension
    assert second.collection_total_points == first.collection_total_points  # no duplicates
    assert first.collection_created is True and second.collection_created is False

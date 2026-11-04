"""Shared pytest fixtures.

A fixture is a helper that pytest creates and passes to a test by argument name.
scope="session" means it is created once and reused by every test (models are slow to load).
"""

import pytest

from config.settings import Settings

MODEL_NAME = Settings().embedding_model_name


@pytest.fixture(scope="session")
def tokenizer():
    from transformers import AutoTokenizer

    return AutoTokenizer.from_pretrained(MODEL_NAME)


@pytest.fixture(scope="session")
def embedding_model():
    from tactiq.indexing.embeddings import EmbeddingModel

    return EmbeddingModel(MODEL_NAME, batch_size=4)

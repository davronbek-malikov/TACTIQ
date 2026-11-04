"""Tests for Embedding Generation (loads the real model, marked slow)."""

import numpy as np
import pytest


@pytest.mark.slow
def test_dimension_comes_from_model_output(embedding_model):
    vectors = embedding_model.embed(["High pressing in the opponent's half."])
    assert vectors.shape == (1, embedding_model.dimension)
    assert embedding_model.dimension > 0


@pytest.mark.slow
def test_batches_give_same_result_as_single_call(embedding_model):
    texts = [f"Counterpressing example {i}" for i in range(10)]  # batch_size=4 -> 3 batches
    vectors = embedding_model.embed(texts)

    assert vectors.shape == (10, embedding_model.dimension)
    single = embedding_model.embed([texts[7]])[0]
    assert np.allclose(vectors[7], single, atol=1e-5)


@pytest.mark.slow
def test_vectors_are_normalised(embedding_model):
    vectors = embedding_model.embed(["Low block", "Build-up play from the back"])
    assert np.allclose(np.linalg.norm(vectors, axis=1), 1.0, atol=1e-5)


@pytest.mark.slow
def test_similar_texts_are_closer(embedding_model):
    press, pressing, tickets = embedding_model.embed(
        ["high press", "aggressive pressing in the opponent's half", "stadium ticket prices"]
    )
    assert press @ pressing > press @ tickets  # dot product = cosine, because vectors are normalised


@pytest.mark.slow
def test_empty_input_and_validation(embedding_model):
    assert embedding_model.embed([]).shape == (0, embedding_model.dimension)
    with pytest.raises(ValueError):
        embedding_model.validate(np.full((1, embedding_model.dimension), np.nan), expected_count=1)
    with pytest.raises(ValueError):
        embedding_model.validate(np.zeros((2, 3)), expected_count=2)

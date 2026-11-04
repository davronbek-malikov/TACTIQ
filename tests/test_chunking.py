"""Tests for Chunking: window maths, chunk size, overlap, stable IDs, no empty chunks."""

import pytest

from tactiq.indexing.chunking import TokenTextSplitter, make_chunk_id, make_token_windows
from tactiq.indexing.document_loading import Document
from tactiq.indexing.metadata import make_document_id

# ---------- pure window maths (no tokenizer needed) ----------


def test_windows_example_from_docstring():
    assert list(make_token_windows(10, chunk_size=4, overlap=1)) == [(0, 4), (3, 7), (6, 10)]


def test_windows_respect_size_and_overlap():
    windows = list(make_token_windows(1200, chunk_size=500, overlap=50))

    assert windows == [(0, 500), (450, 950), (900, 1200)]
    for (start_a, end_a), (start_b, _end_b) in zip(windows, windows[1:]):
        assert end_a - start_b == 50          # exactly `overlap` tokens are shared
    assert all(end - start <= 500 for start, end in windows)
    assert windows[-1][1] == 1200            # the last token is covered


def test_short_text_gives_one_window_and_empty_text_none():
    assert list(make_token_windows(30, 500, 50)) == [(0, 30)]
    assert list(make_token_windows(0, 500, 50)) == []


def test_text_exactly_chunk_size_gives_one_window():
    assert list(make_token_windows(500, 500, 50)) == [(0, 500)]


@pytest.mark.parametrize("chunk_size, overlap", [(0, 0), (-5, 0), (100, 100), (100, 150), (100, -1)])
def test_invalid_settings_raise(chunk_size, overlap):
    with pytest.raises(ValueError):
        list(make_token_windows(10, chunk_size, overlap))


def test_chunk_id_is_stable_and_unique():
    document_id = make_document_id("tactics/press.pdf")
    assert make_chunk_id(document_id, 1, 0) == make_chunk_id(document_id, 1, 0)
    assert make_chunk_id(document_id, 1, 0) != make_chunk_id(document_id, 1, 1)
    assert make_chunk_id(document_id, 1, 0) != make_chunk_id(document_id, 2, 0)


# ---------- with the real tokenizer ----------


def make_document(text, page=None):
    return Document(
        text=text,
        metadata={
            "document_id": make_document_id("tactics/build_up.md"),
            "source": "build_up.md",
            "source_path": "tactics/build_up.md",
            "file_type": "md",
            "page": page,
            "topic": "build_up_play",
        },
    )


@pytest.mark.slow
def test_chunks_respect_token_limit_and_overlap(tokenizer):
    text = " ".join(f"Build-up phase {i} uses a third-man combination." for i in range(200))
    splitter = TokenTextSplitter(tokenizer, chunk_size=100, chunk_overlap=20)

    pieces = splitter.split_text(text)

    assert len(pieces) > 1
    for chunk_text, token_count in pieces:
        assert chunk_text.strip() != ""
        assert token_count <= 100
        assert len(tokenizer.encode(chunk_text, add_special_tokens=False)) <= 100

    # The end of chunk 1 reappears at the start of chunk 2 (overlap).
    first_tokens = tokenizer.encode(pieces[0][0], add_special_tokens=False)
    second_tokens = tokenizer.encode(pieces[1][0], add_special_tokens=False)
    assert first_tokens[-20:] == second_tokens[:20]


@pytest.mark.slow
def test_chunk_text_is_original_text_not_lowercased(tokenizer):
    text = "Gündoğan Plays In A 4-3-3 Under HIGH Pressure."
    splitter = TokenTextSplitter(tokenizer, chunk_size=500, chunk_overlap=50)

    assert splitter.split_text(text) == [(text, len(tokenizer.encode(text, add_special_tokens=False)))]


@pytest.mark.slow
def test_split_document_preserves_metadata_and_ids(tokenizer):
    splitter = TokenTextSplitter(tokenizer, chunk_size=50, chunk_overlap=10)
    document = make_document("Counterpressing after a loss of possession. " * 40, page=3)

    chunks = splitter.split_document(document)
    chunks_again = splitter.split_document(document)

    assert len(chunks) > 1
    assert [c.chunk_id for c in chunks] == [c.chunk_id for c in chunks_again]   # stable
    assert len({c.chunk_id for c in chunks}) == len(chunks)                      # unique
    for index, chunk in enumerate(chunks):
        assert chunk.document_id == document.metadata["document_id"]
        assert chunk.metadata["source"] == "build_up.md"
        assert chunk.metadata["page"] == 3
        assert chunk.metadata["topic"] == "build_up_play"
        assert chunk.metadata["chunk_index"] == index


@pytest.mark.slow
def test_empty_document_gives_no_chunks(tokenizer):
    splitter = TokenTextSplitter(tokenizer)
    assert splitter.split_document(make_document("")) == []


@pytest.mark.slow
def test_invalid_overlap_rejected_by_splitter(tokenizer):
    with pytest.raises(ValueError):
        TokenTextSplitter(tokenizer, chunk_size=50, chunk_overlap=50)

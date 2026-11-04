"""Tests for metadata: stable document IDs, sidecar files, no fabricated values, preservation."""

import json

from tactiq.indexing.chunking import Chunk
from tactiq.indexing.document_loading import Document, load_file
from tactiq.indexing.metadata import OPTIONAL_FIELDS, attach_metadata, build_metadata, make_document_id
from tactiq.indexing.text_cleaning import clean_document
from tactiq.indexing.vector_store import build_payload

EXPECTED_KEYS = {
    "document_id", "source", "source_path", "file_type", "page",
    "document_type", "topic", "language", "match_id", "team_id", "player_id",
}


def loaded_document(tmp_path, name="press.txt", text="High press"):
    (tmp_path / name).write_text(text, encoding="utf-8")
    return load_file(tmp_path / name, tmp_path)[0]


def test_document_id_is_stable_and_depends_on_path():
    assert make_document_id("a/press.pdf") == make_document_id("a/press.pdf")
    assert make_document_id("a/press.pdf") != make_document_id("b/press.pdf")


def test_unknown_metadata_defaults_to_none(tmp_path):
    metadata = build_metadata(loaded_document(tmp_path), tmp_path)

    assert set(metadata) == EXPECTED_KEYS
    for key in OPTIONAL_FIELDS:
        assert metadata[key] is None  # nothing is guessed
    assert metadata["source"] == "press.txt"
    assert metadata["file_type"] == "txt"


def test_sidecar_metadata_is_used_and_unknown_keys_ignored(tmp_path):
    document = loaded_document(tmp_path)
    sidecar = {"document_type": "tactical_report", "topic": "high_pressing", "language": "en",
               "team_id": "team-123", "made_up_field": "ignored"}
    (tmp_path / "press.txt.meta.json").write_text(json.dumps(sidecar), encoding="utf-8")

    metadata = build_metadata(document, tmp_path)

    assert metadata["document_type"] == "tactical_report"
    assert metadata["topic"] == "high_pressing"
    assert metadata["team_id"] == "team-123"
    assert metadata["match_id"] is None
    assert "made_up_field" not in metadata


def test_metadata_survives_cleaning_and_payload(tmp_path):
    document = attach_metadata(clean_document(loaded_document(tmp_path, text="  High   press  ")), tmp_path)
    chunk = Chunk(chunk_id="c1", document_id=document.metadata["document_id"], text=document.text,
                  metadata={**document.metadata, "chunk_index": 0, "token_count": 2})

    payload = build_payload(chunk, "test-model")

    assert document.text == "High press"
    assert payload["chunk_text"] == "High press"
    assert payload["document_id"] == make_document_id("press.txt")
    assert payload["source"] == "press.txt"
    assert payload["embedding_model"] == "test-model"
    for key in ["match_id", "team_id", "player_id", "page", "topic"]:
        assert key in payload and payload[key] is None


def test_attach_metadata_does_not_change_text():
    document = Document(text="Low block", metadata={"source": "x.txt", "source_path": "x.txt",
                                                    "file_type": "txt", "page": None})
    assert attach_metadata(document).text == "Low block"

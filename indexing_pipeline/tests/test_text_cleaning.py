"""Tests for Text Cleaning."""

from indexing.step1_document_loading import Document
from indexing.step3_text_cleaning import CleaningConfig, clean_document, clean_text


def test_collapses_spaces_and_trims_lines():
    assert clean_text("  High    press \t in   a 4-3-3  ") == "High press in a 4-3-3"


def test_collapses_many_blank_lines_but_keeps_paragraphs():
    text = "Paragraph one.\n\n\n\n\nParagraph two.\nSame paragraph."
    assert clean_text(text) == "Paragraph one.\n\nParagraph two.\nSame paragraph."


def test_removes_control_characters_and_normalises_line_endings():
    text = "Counter\x00press\x07ing\r\nnext line\rlast"
    assert clean_text(text) == "Counterpressing\nnext line\nlast"


def test_preserves_football_terms_punctuation_and_names():
    text = "xG: 1.7? No — Gündoğan's 4-2-3-1 (PPDA 9.5)!"
    assert clean_text(text) == text


def test_replaces_non_breaking_spaces_and_normalises_unicode():
    decomposed = "Gu\u0308ndog\u0306an\u00a0pressing"  # "ü" and "ğ" written as letter + accent
    assert clean_text(decomposed) == "Gündoğan pressing"


def test_empty_and_whitespace_only_text():
    assert clean_text("") == ""
    assert clean_text(" \n\t \n ") == ""


def test_config_can_disable_steps():
    config = CleaningConfig(collapse_spaces=False, collapse_newlines=False)
    assert clean_text("a   b\n\n\n\nc", config) == "a   b\n\n\n\nc"


def test_clean_document_preserves_metadata_and_does_not_modify_input():
    original = Document(text="  Low   block  ", metadata={"source": "low_block.txt", "page": None})
    cleaned = clean_document(original)

    assert cleaned.text == "Low block"
    assert cleaned.metadata == original.metadata
    assert cleaned.metadata is not original.metadata  # a copy, not the same dict
    assert original.text == "  Low   block  "

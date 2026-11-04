"""Tests for Document Loading: TXT, Markdown, PDF, DOCX, empty, unsupported and corrupted files."""

import pymupdf
import pytest
from docx import Document as DocxFile

from tactiq.indexing.document_loading import discover_files, load_directory, load_file


def make_pdf(path, page_texts):
    pdf = pymupdf.open()
    for text in page_texts:
        page = pdf.new_page()
        if text:
            page.insert_text((72, 72), text)
    pdf.save(path)
    pdf.close()


def test_load_txt(tmp_path):
    (tmp_path / "notes.txt").write_text("Low block in a 4-4-2.", encoding="utf-8")
    documents = load_file(tmp_path / "notes.txt", tmp_path)

    assert len(documents) == 1
    assert documents[0].text == "Low block in a 4-4-2."
    assert documents[0].metadata == {
        "source": "notes.txt",
        "source_path": "notes.txt",
        "file_type": "txt",
        "page": None,
    }


def test_load_markdown_keeps_non_ascii_names(tmp_path):
    (tmp_path / "press.md").write_text("# High press\nGündoğan and Ødegaard", encoding="utf-8")
    documents = load_file(tmp_path / "press.md", tmp_path)

    assert documents[0].metadata["file_type"] == "md"
    assert "Gündoğan and Ødegaard" in documents[0].text


def test_load_pdf_one_document_per_page(tmp_path):
    make_pdf(tmp_path / "report.pdf", ["Page one counterpress", "Page two rest defence"])
    documents = load_file(tmp_path / "report.pdf", tmp_path)

    assert [doc.metadata["page"] for doc in documents] == [1, 2]
    assert "Page one counterpress" in documents[0].text
    assert "Page two rest defence" in documents[1].text


def test_load_docx_includes_tables(tmp_path):
    docx = DocxFile()
    docx.add_paragraph("High pressing summary")
    table = docx.add_table(rows=1, cols=2)
    table.rows[0].cells[0].text = "Advantage"
    table.rows[0].cells[1].text = "Risk"
    docx.save(tmp_path / "press.docx")

    documents = load_file(tmp_path / "press.docx", tmp_path)

    assert "High pressing summary" in documents[0].text
    assert "Advantage | Risk" in documents[0].text
    assert documents[0].metadata["page"] is None


def test_discover_is_recursive_and_ignores_hidden_and_sidecar_files(tmp_path):
    (tmp_path / "reports" / "2026").mkdir(parents=True)
    (tmp_path / "reports" / "2026" / "a.txt").write_text("a", encoding="utf-8")
    (tmp_path / ".gitkeep").write_text("", encoding="utf-8")
    (tmp_path / "a.txt.meta.json").write_text("{}", encoding="utf-8")

    found = [path.relative_to(tmp_path).as_posix() for path in discover_files(tmp_path)]

    assert found == ["reports/2026/a.txt"]


def test_load_directory_handles_empty_unsupported_and_corrupted_files(tmp_path):
    (tmp_path / "good.txt").write_text("Build-up play", encoding="utf-8")
    (tmp_path / "empty.txt").write_text("", encoding="utf-8")
    (tmp_path / "image.png").write_bytes(b"\x89PNG")
    (tmp_path / "broken.pdf").write_bytes(b"this is not a pdf")

    result = load_directory(tmp_path)

    # Empty files are loaded (the cleaning step decides they are empty and skips them).
    assert sorted(result.loaded_files) == ["empty.txt", "good.txt"]
    assert result.skipped_files == ["image.png"]
    assert list(result.failed_files) == ["broken.pdf"]


def test_unsupported_extension_raises(tmp_path):
    (tmp_path / "video.mp4").write_bytes(b"")
    with pytest.raises(ValueError):
        load_file(tmp_path / "video.mp4", tmp_path)


def test_missing_directory_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_directory(tmp_path / "does_not_exist")

import pytest
import sys
import os
from pathlib import Path
from unittest import mock
import zipfile

# Add the helpers directory to sys.path so we can import simplify_redlines
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts/office/helpers')))

from simplify_redlines import simplify_redlines, infer_author, _get_authors_from_docx, get_tracked_change_authors

def test_simplify_redlines_malformed_xml(tmp_path: Path):
    word_dir = tmp_path / "word"
    word_dir.mkdir()
    doc_xml = word_dir / "document.xml"

    # Write malformed XML (unbound prefix or mismatched tags)
    doc_xml.write_text("<w:document><w:body><w:p>Unclosed paragraph</w:body></w:document>", encoding="utf-8")

    count, msg = simplify_redlines(str(tmp_path))

    assert count == 0
    assert msg.startswith("Error: ")

@mock.patch("simplify_redlines.defusedxml.minidom.parseString")
def test_simplify_redlines_mocked_error(mock_parseString, tmp_path: Path):
    mock_parseString.side_effect = Exception("mocked parse error")
    word_dir = tmp_path / "word"
    word_dir.mkdir()
    doc_xml = word_dir / "document.xml"
    doc_xml.write_text("<w:document></w:document>", encoding="utf-8")

    count, msg = simplify_redlines(str(tmp_path))

    assert count == 0
    assert msg == "Error: mocked parse error"

@mock.patch("simplify_redlines.get_tracked_change_authors")
@mock.patch("simplify_redlines._get_authors_from_docx")
def test_infer_author_multiple_authors(mock_get_authors_from_docx, mock_get_tracked_change_authors, tmp_path: Path):
    mock_get_tracked_change_authors.return_value = {"AuthorA": 2, "AuthorB": 3}
    mock_get_authors_from_docx.return_value = {"AuthorA": 1, "AuthorB": 1}

    with pytest.raises(ValueError, match="Multiple authors added new changes"):
        infer_author(tmp_path, tmp_path / "dummy.docx")

@mock.patch("simplify_redlines.zipfile.ZipFile")
def test_get_authors_from_docx_bad_zip(mock_zipfile, tmp_path: Path):
    mock_zipfile.side_effect = zipfile.BadZipFile("bad zip")

    authors = _get_authors_from_docx(tmp_path / "dummy.docx")
    assert authors == {}

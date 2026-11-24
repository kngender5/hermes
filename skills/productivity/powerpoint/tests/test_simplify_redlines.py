import pytest
import sys
import os
from pathlib import Path

# Add the helpers directory to sys.path so we can import simplify_redlines
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts/office/helpers')))

from simplify_redlines import simplify_redlines

def test_simplify_redlines_malformed_xml(tmp_path: Path):
    word_dir = tmp_path / "word"
    word_dir.mkdir()
    doc_xml = word_dir / "document.xml"

    # Write malformed XML (unbound prefix or mismatched tags)
    doc_xml.write_text("<w:document><w:body><w:p>Unclosed paragraph</w:body></w:document>", encoding="utf-8")

    count, msg = simplify_redlines(str(tmp_path))

    assert count == 0
    assert msg.startswith("Error: ")

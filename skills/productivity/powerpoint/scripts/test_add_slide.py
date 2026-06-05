import pytest
import sys
from pathlib import Path
from add_slide import create_slide_from_layout

@pytest.fixture
def mock_unpacked_dir(tmp_path):
    unpacked_dir = tmp_path / "unpacked"
    unpacked_dir.mkdir()

    # Create slideLayouts
    layouts_dir = unpacked_dir / "ppt" / "slideLayouts"
    layouts_dir.mkdir(parents=True)
    (layouts_dir / "slideLayout1.xml").write_text("<xml/>", encoding="utf-8")

    # Create slides dir
    slides_dir = unpacked_dir / "ppt" / "slides"
    slides_dir.mkdir(parents=True)
    (slides_dir / "slide1.xml").write_text("<xml/>", encoding="utf-8")

    # Create [Content_Types].xml
    (unpacked_dir / "[Content_Types].xml").write_text("<Types>\n</Types>", encoding="utf-8")

    # Create presentation.xml.rels
    pres_rels_dir = unpacked_dir / "ppt" / "_rels"
    pres_rels_dir.mkdir(parents=True)
    (pres_rels_dir / "presentation.xml.rels").write_text('<Relationships>\n  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide1.xml"/>\n</Relationships>', encoding="utf-8")

    # Create presentation.xml
    (unpacked_dir / "ppt" / "presentation.xml").write_text('<xml><p:sldIdLst><p:sldId id="256" r:id="rId1"/></p:sldIdLst></xml>', encoding="utf-8")

    return unpacked_dir

def test_create_slide_from_layout_success(mock_unpacked_dir, capsys):
    create_slide_from_layout(mock_unpacked_dir, "slideLayout1.xml")

    # Check slide2.xml is created
    dest_slide = mock_unpacked_dir / "ppt" / "slides" / "slide2.xml"
    assert dest_slide.exists()
    assert "p:sld" in dest_slide.read_text(encoding="utf-8")

    # Check slide2.xml.rels is created
    dest_rels = mock_unpacked_dir / "ppt" / "slides" / "_rels" / "slide2.xml.rels"
    assert dest_rels.exists()
    assert "slideLayout1.xml" in dest_rels.read_text(encoding="utf-8")

    # Check [Content_Types].xml is updated
    content_types = (mock_unpacked_dir / "[Content_Types].xml").read_text(encoding="utf-8")
    assert "/ppt/slides/slide2.xml" in content_types

    # Check presentation.xml.rels is updated
    pres_rels = (mock_unpacked_dir / "ppt" / "_rels" / "presentation.xml.rels").read_text(encoding="utf-8")
    assert 'Target="slides/slide2.xml"' in pres_rels

    # Check standard output
    captured = capsys.readouterr()
    assert "Created slide2.xml from slideLayout1.xml" in captured.out
    assert 'Add to presentation.xml <p:sldIdLst>: <p:sldId id="257" r:id="rId2"/>' in captured.out

def test_create_slide_from_layout_missing_layout(mock_unpacked_dir, capsys):
    with pytest.raises(SystemExit) as exc_info:
        create_slide_from_layout(mock_unpacked_dir, "nonexistent.xml")

    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "Error:" in captured.err
    assert "nonexistent.xml not found" in captured.err


def test_create_slide_from_layout_invalid_unpacked_dir(tmp_path, capsys):
    # Pass a valid layout file string, but the unpacked directory lacks necessary subdirectories
    unpacked_dir = tmp_path / "invalid_unpacked"
    unpacked_dir.mkdir()

    # create_slide_from_layout expects ppt/slideLayouts to exist for the layout file check,
    # but the layout file itself won't exist.
    # It also expects get_next_slide_number to look in ppt/slides.

    with pytest.raises(SystemExit) as exc_info:
        create_slide_from_layout(unpacked_dir, "slideLayout1.xml")

    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "Error:" in captured.err
    assert "slideLayout1.xml not found" in captured.err

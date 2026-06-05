import pytest
import sys
import shutil
from unittest.mock import patch
from pathlib import Path
import re

# Add scripts directory to sys.path so we can import add_slide
sys.path.append(str(Path(__file__).parent.parent / "scripts"))

import add_slide

def test_parse_source():
    # Test layout
    assert add_slide.parse_source("slideLayout1.xml") == ("layout", "slideLayout1.xml")
    assert add_slide.parse_source("slideLayout2.xml") == ("layout", "slideLayout2.xml")

    # Test slide
    assert add_slide.parse_source("slide1.xml") == ("slide", None)
    assert add_slide.parse_source("slide2.xml") == ("slide", None)
    assert add_slide.parse_source("some_other_file.xml") == ("slide", None)

def test_get_next_slide_number(tmp_path):
    # Empty dir
    assert add_slide.get_next_slide_number(tmp_path) == 1

    # Existing slides
    (tmp_path / "slide1.xml").touch()
    assert add_slide.get_next_slide_number(tmp_path) == 2

    (tmp_path / "slide5.xml").touch()
    assert add_slide.get_next_slide_number(tmp_path) == 6

    # Ignore non-matching files
    (tmp_path / "slide_master.xml").touch()
    (tmp_path / "slide.xml").touch()
    (tmp_path / "slide05.xml").touch() # match group is '05' -> int(5) -> max is still 5
    assert add_slide.get_next_slide_number(tmp_path) == 6

def setup_mock_unpacked_dir(tmp_path):
    unpacked = tmp_path / "unpacked"
    unpacked.mkdir()

    # Create [Content_Types].xml
    (unpacked / "[Content_Types].xml").write_text('''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="xml" ContentType="application/xml"/>
</Types>''', encoding="utf-8")

    # Create ppt dir
    ppt = unpacked / "ppt"
    ppt.mkdir()

    # Create presentation.xml
    (ppt / "presentation.xml").write_text('''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:sldIdLst>
    <p:sldId id="256" r:id="rId2"/>
  </p:sldIdLst>
</p:presentation>''', encoding="utf-8")

    # Create _rels/presentation.xml.rels
    pres_rels_dir = ppt / "_rels"
    pres_rels_dir.mkdir()
    (pres_rels_dir / "presentation.xml.rels").write_text('''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide1.xml"/>
</Relationships>''', encoding="utf-8")

    # Create slides dir
    slides_dir = ppt / "slides"
    slides_dir.mkdir()
    (slides_dir / "slide1.xml").write_text("<slide/>", encoding="utf-8")

    # Create slides/_rels dir
    slides_rels_dir = slides_dir / "_rels"
    slides_rels_dir.mkdir()
    (slides_rels_dir / "slide1.xml.rels").write_text('''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesSlide" Target="../notesSlides/notesSlide1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
</Relationships>''', encoding="utf-8")

    # Create slideLayouts dir
    layouts_dir = ppt / "slideLayouts"
    layouts_dir.mkdir()
    (layouts_dir / "slideLayout1.xml").write_text("<layout/>", encoding="utf-8")

    return unpacked

def test_create_slide_from_layout(tmp_path, capsys):
    unpacked = setup_mock_unpacked_dir(tmp_path)

    add_slide.create_slide_from_layout(unpacked, "slideLayout1.xml")

    # Check outputs
    slides_dir = unpacked / "ppt" / "slides"
    assert (slides_dir / "slide2.xml").exists()
    assert (slides_dir / "_rels" / "slide2.xml.rels").exists()

    # Check rels content
    rels_content = (slides_dir / "_rels" / "slide2.xml.rels").read_text(encoding="utf-8")
    assert 'Target="../slideLayouts/slideLayout1.xml"' in rels_content

    # Check content types
    content_types = (unpacked / "[Content_Types].xml").read_text(encoding="utf-8")
    assert 'PartName="/ppt/slides/slide2.xml"' in content_types
    assert 'ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"' in content_types

    # Check presentation rels
    pres_rels = (unpacked / "ppt" / "_rels" / "presentation.xml.rels").read_text(encoding="utf-8")
    assert 'Target="slides/slide2.xml"' in pres_rels

    out, err = capsys.readouterr()
    assert "Created slide2.xml from slideLayout1.xml" in out
    assert 'Add to presentation.xml <p:sldIdLst>: <p:sldId id="257" r:id="rId3"/>' in out

def test_create_slide_from_layout_missing(tmp_path, capsys):
    unpacked = setup_mock_unpacked_dir(tmp_path)

    with pytest.raises(SystemExit) as e:
        add_slide.create_slide_from_layout(unpacked, "slideLayout99.xml")

    assert e.value.code == 1
    out, err = capsys.readouterr()
    assert "Error:" in err
    assert "slideLayout99.xml not found" in err

@patch("add_slide.shutil.copy2")
def test_duplicate_slide(mock_copy2, tmp_path, capsys):
    unpacked = setup_mock_unpacked_dir(tmp_path)

    slides_dir = unpacked / "ppt" / "slides"
    rels_dir = slides_dir / "_rels"

    # We need to simulate copy2 actually creating the destination files so that subsequent code
    # (like reading dest_rels) works correctly.
    def mock_copy2_side_effect(src, dst):
        shutil.copyfile(src, dst)

    mock_copy2.side_effect = mock_copy2_side_effect

    add_slide.duplicate_slide(unpacked, "slide1.xml")

    # Check that copy2 was called as our external dependency
    assert mock_copy2.call_count == 2
    mock_copy2.assert_any_call(slides_dir / "slide1.xml", slides_dir / "slide2.xml")
    mock_copy2.assert_any_call(rels_dir / "slide1.xml.rels", rels_dir / "slide2.xml.rels")

    # Check outputs
    assert (slides_dir / "slide2.xml").exists()
    assert (slides_dir / "slide2.xml").read_text(encoding="utf-8") == "<slide/>"

    # Check rels
    rels_path = slides_dir / "_rels" / "slide2.xml.rels"
    assert rels_path.exists()
    rels_content = rels_path.read_text(encoding="utf-8")
    # notesSlide relationship should be removed
    assert 'notesSlide' not in rels_content
    assert 'slideLayout1.xml' in rels_content

    # Check content types
    content_types = (unpacked / "[Content_Types].xml").read_text(encoding="utf-8")
    assert 'PartName="/ppt/slides/slide2.xml"' in content_types

    # Check presentation rels
    pres_rels = (unpacked / "ppt" / "_rels" / "presentation.xml.rels").read_text(encoding="utf-8")
    assert 'Target="slides/slide2.xml"' in pres_rels

    out, err = capsys.readouterr()
    assert "Created slide2.xml from slide1.xml" in out
    assert 'Add to presentation.xml <p:sldIdLst>: <p:sldId id="257" r:id="rId3"/>' in out

def test_duplicate_slide_missing(tmp_path, capsys):
    unpacked = setup_mock_unpacked_dir(tmp_path)

    with pytest.raises(SystemExit) as e:
        add_slide.duplicate_slide(unpacked, "slide99.xml")

    assert e.value.code == 1
    out, err = capsys.readouterr()
    assert "Error:" in err
    assert "slide99.xml not found" in err

def test_duplicate_slide_no_rels(tmp_path):
    unpacked = setup_mock_unpacked_dir(tmp_path)

    # Remove rels for slide1
    (unpacked / "ppt" / "slides" / "_rels" / "slide1.xml.rels").unlink()

    add_slide.duplicate_slide(unpacked, "slide1.xml")

    slides_dir = unpacked / "ppt" / "slides"
    assert (slides_dir / "slide2.xml").exists()
    assert not (slides_dir / "_rels" / "slide2.xml.rels").exists()

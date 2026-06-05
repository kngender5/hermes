import sys
from pathlib import Path

import pytest

from skills.productivity.powerpoint.scripts.add_slide import (
    create_slide_from_layout,
    duplicate_slide,
)


@pytest.fixture
def unpacked_dir(tmp_path: Path) -> Path:
    """Fixture to set up a dummy unpacked PPTX directory."""
    # Create directory structure
    (tmp_path / "ppt" / "slides" / "_rels").mkdir(parents=True)
    (tmp_path / "ppt" / "slideLayouts").mkdir(parents=True)
    (tmp_path / "ppt" / "_rels").mkdir(parents=True)

    # Base files
    (tmp_path / "[Content_Types].xml").write_text(
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Types>\n</Types>',
        encoding="utf-8",
    )
    (tmp_path / "ppt" / "presentation.xml").write_text(
        '<p:presentation><p:sldIdLst><p:sldId id="256" r:id="rId1"/></p:sldIdLst></p:presentation>',
        encoding="utf-8",
    )
    (tmp_path / "ppt" / "_rels" / "presentation.xml.rels").write_text(
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Relationships>\n</Relationships>',
        encoding="utf-8",
    )

    # Dummy layout and slide
    (tmp_path / "ppt" / "slideLayouts" / "slideLayout1.xml").write_text(
        "<layout/>", encoding="utf-8"
    )
    (tmp_path / "ppt" / "slides" / "slide1.xml").write_text("<slide/>", encoding="utf-8")

    # slide.rels with notesSlide relationship
    rels_content = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships>
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesSlide" Target="../notesSlides/notesSlide1.xml"/>
</Relationships>"""
    (tmp_path / "ppt" / "slides" / "_rels" / "slide1.xml.rels").write_text(
        rels_content, encoding="utf-8"
    )

    return tmp_path


def test_create_slide_from_layout_success(unpacked_dir: Path) -> None:
    create_slide_from_layout(unpacked_dir, "slideLayout1.xml")

    # Verify slide is created
    dest_slide = unpacked_dir / "ppt" / "slides" / "slide2.xml"
    assert dest_slide.exists()

    # Verify .rels is created and points to layout
    dest_rels = unpacked_dir / "ppt" / "slides" / "_rels" / "slide2.xml.rels"
    assert dest_rels.exists()
    rels_text = dest_rels.read_text(encoding="utf-8")
    assert "slideLayout1.xml" in rels_text

    # Verify Content_Types updated
    content_types = (unpacked_dir / "[Content_Types].xml").read_text(encoding="utf-8")
    assert 'PartName="/ppt/slides/slide2.xml"' in content_types

    # Verify presentation rels updated
    pres_rels = (unpacked_dir / "ppt" / "_rels" / "presentation.xml.rels").read_text(encoding="utf-8")
    assert 'Target="slides/slide2.xml"' in pres_rels


def test_create_slide_from_layout_failure(unpacked_dir: Path, capsys: pytest.CaptureFixture) -> None:
    with pytest.raises(SystemExit) as exc_info:
        create_slide_from_layout(unpacked_dir, "missingLayout.xml")

    assert exc_info.value.code == 1

    captured = capsys.readouterr()
    assert "not found" in captured.err
    assert "missingLayout.xml" in captured.err


def test_duplicate_slide_success(unpacked_dir: Path) -> None:
    duplicate_slide(unpacked_dir, "slide1.xml")

    # Verify duplicate slide created
    dest_slide = unpacked_dir / "ppt" / "slides" / "slide2.xml"
    assert dest_slide.exists()

    # Verify .rels copied and notesSlide dropped
    dest_rels = unpacked_dir / "ppt" / "slides" / "_rels" / "slide2.xml.rels"
    assert dest_rels.exists()
    rels_text = dest_rels.read_text(encoding="utf-8")
    assert "notesSlide" not in rels_text
    assert "slideLayout1.xml" in rels_text

    # Verify Content_Types updated
    content_types = (unpacked_dir / "[Content_Types].xml").read_text(encoding="utf-8")
    assert 'PartName="/ppt/slides/slide2.xml"' in content_types

    # Verify presentation rels updated
    pres_rels = (unpacked_dir / "ppt" / "_rels" / "presentation.xml.rels").read_text(encoding="utf-8")
    assert 'Target="slides/slide2.xml"' in pres_rels


def test_duplicate_slide_failure(unpacked_dir: Path, capsys: pytest.CaptureFixture) -> None:
    with pytest.raises(SystemExit) as exc_info:
        duplicate_slide(unpacked_dir, "missingSlide.xml")

    assert exc_info.value.code == 1

    captured = capsys.readouterr()
    assert "not found" in captured.err
    assert "missingSlide.xml" in captured.err

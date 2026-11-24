import pytest
from pathlib import Path
from clean import (
    get_slides_in_sldidlst,
    remove_orphaned_slides,
    remove_trash_directory,
    get_slide_referenced_files,
    remove_orphaned_rels_files,
    get_referenced_files,
    remove_orphaned_files,
    update_content_types,
    clean_unused_files,
)

def test_get_slides_in_sldidlst(tmp_path: Path):
    ppt_dir = tmp_path / "ppt"
    rels_dir = ppt_dir / "_rels"
    rels_dir.mkdir(parents=True)

    pres_path = ppt_dir / "presentation.xml"
    pres_rels_path = rels_dir / "presentation.xml.rels"

    # Missing files
    assert get_slides_in_sldidlst(tmp_path) == set()

    pres_rels_path.write_text(
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide1.xml"/>'
        '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide2.xml"/>'
        '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="theme/theme1.xml"/>'
        '</Relationships>'
    )
    pres_path.write_text(
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        '<p:sldIdLst>'
        '<p:sldId id="256" r:id="rId1"/>'
        '</p:sldIdLst>'
        '</p:presentation>'
    )

    assert get_slides_in_sldidlst(tmp_path) == {"slide1.xml"}


def test_remove_orphaned_slides(tmp_path: Path):
    ppt_dir = tmp_path / "ppt"
    slides_dir = ppt_dir / "slides"
    slides_rels_dir = slides_dir / "_rels"
    slides_rels_dir.mkdir(parents=True)

    pres_rels_dir = ppt_dir / "_rels"
    pres_rels_dir.mkdir(parents=True)

    pres_rels_path = pres_rels_dir / "presentation.xml.rels"
    pres_path = ppt_dir / "presentation.xml"

    pres_rels_path.write_text(
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide1.xml"/>'
        '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide2.xml"/>'
        '</Relationships>'
    )
    pres_path.write_text(
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        '<p:sldIdLst>'
        '<p:sldId id="256" r:id="rId1"/>'
        '</p:sldIdLst>'
        '</p:presentation>'
    )

    slide1 = slides_dir / "slide1.xml"
    slide2 = slides_dir / "slide2.xml"
    slide1_rels = slides_rels_dir / "slide1.xml.rels"
    slide2_rels = slides_rels_dir / "slide2.xml.rels"

    slide1.write_text("<test/>")
    slide2.write_text("<test/>")
    slide1_rels.write_text("<test/>")
    slide2_rels.write_text("<test/>")

    removed = remove_orphaned_slides(tmp_path)

    assert slide1.exists()
    assert slide1_rels.exists()
    assert not slide2.exists()
    assert not slide2_rels.exists()

    assert set(removed) == {
        "ppt/slides/slide2.xml",
        "ppt/slides/_rels/slide2.xml.rels"
    }

    updated_rels = pres_rels_path.read_text()
    assert "slide1.xml" in updated_rels
    assert "slide2.xml" not in updated_rels


def test_remove_trash_directory(tmp_path: Path):
    trash_dir = tmp_path / "[trash]"
    trash_dir.mkdir()

    file1 = trash_dir / "file1.txt"
    file2 = trash_dir / "file2.xml"

    file1.write_text("test")
    file2.write_text("test")

    removed = remove_trash_directory(tmp_path)

    assert not file1.exists()
    assert not file2.exists()
    assert not trash_dir.exists()
    assert set(removed) == {"[trash]/file1.txt", "[trash]/file2.xml"}


def test_get_slide_referenced_files(tmp_path: Path):
    slides_rels_dir = tmp_path / "ppt" / "slides" / "_rels"
    slides_rels_dir.mkdir(parents=True)

    rels_file = slides_rels_dir / "slide1.xml.rels"
    rels_file.write_text(
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="type1" Target="../media/image1.png"/>'
        '<Relationship Id="rId2" Type="type2" Target="../notesSlides/notes1.xml"/>'
        '</Relationships>'
    )

    refs = get_slide_referenced_files(tmp_path)
    assert refs == {Path("ppt/media/image1.png"), Path("ppt/notesSlides/notes1.xml")}


def test_remove_orphaned_rels_files(tmp_path: Path):
    slides_rels_dir = tmp_path / "ppt" / "slides" / "_rels"
    slides_rels_dir.mkdir(parents=True)

    slide_rels = slides_rels_dir / "slide1.xml.rels"
    slide_rels.write_text(
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="type1" Target="../charts/chart1.xml"/>'
        '</Relationships>'
    )

    charts_dir = tmp_path / "ppt" / "charts"
    charts_rels_dir = charts_dir / "_rels"
    charts_rels_dir.mkdir(parents=True)

    chart1 = charts_dir / "chart1.xml"
    chart1.write_text("<test/>")
    chart1_rels = charts_rels_dir / "chart1.xml.rels"
    chart1_rels.write_text("<test/>")

    chart2 = charts_dir / "chart2.xml"
    chart2_rels = charts_rels_dir / "chart2.xml.rels"
    chart2_rels.write_text("<test/>")

    removed = remove_orphaned_rels_files(tmp_path)

    assert chart1_rels.exists()
    assert not chart2_rels.exists()
    assert set(removed) == {"ppt/charts/_rels/chart2.xml.rels"}


def test_get_referenced_files(tmp_path: Path):
    ppt_dir = tmp_path / "ppt"
    rels_dir = ppt_dir / "_rels"
    rels_dir.mkdir(parents=True)

    pres_rels_path = rels_dir / "presentation.xml.rels"
    pres_rels_path.write_text(
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="slide" Target="slides/slide1.xml"/>'
        '<Relationship Id="rId2" Type="theme" Target="theme/theme1.xml"/>'
        '</Relationships>'
    )

    refs = get_referenced_files(tmp_path)
    assert refs == {Path("ppt/slides/slide1.xml"), Path("ppt/theme/theme1.xml")}


def test_remove_orphaned_files(tmp_path: Path):
    ppt_dir = tmp_path / "ppt"

    media_dir = ppt_dir / "media"
    media_dir.mkdir(parents=True)
    media1 = media_dir / "image1.png"
    media2 = media_dir / "image2.png"
    media1.write_text("test")
    media2.write_text("test")

    theme_dir = ppt_dir / "theme"
    theme_rels_dir = theme_dir / "_rels"
    theme_rels_dir.mkdir(parents=True)
    theme1 = theme_dir / "theme1.xml"
    theme2 = theme_dir / "theme2.xml"
    theme1.write_text("test")
    theme2.write_text("test")
    theme2_rels = theme_rels_dir / "theme2.xml.rels"
    theme2_rels.write_text("test")

    notes_dir = ppt_dir / "notesSlides"
    notes_rels_dir = notes_dir / "_rels"
    notes_rels_dir.mkdir(parents=True)
    notes1 = notes_dir / "notesSlide1.xml"
    notes2 = notes_dir / "notesSlide2.xml"
    notes1.write_text("test")
    notes2.write_text("test")
    notes2_rels = notes_rels_dir / "notesSlide2.xml.rels"
    notes2_rels.write_text("test")

    referenced = {
        Path("ppt/media/image1.png"),
        Path("ppt/theme/theme1.xml"),
        Path("ppt/notesSlides/notesSlide1.xml")
    }

    removed = remove_orphaned_files(tmp_path, referenced)

    assert media1.exists()
    assert not media2.exists()
    assert theme1.exists()
    assert not theme2.exists()
    assert not theme2_rels.exists()
    assert notes1.exists()
    assert not notes2.exists()
    assert not notes2_rels.exists()

    assert set(removed) == {
        "ppt/media/image2.png",
        "ppt/theme/theme2.xml",
        "ppt/theme/_rels/theme2.xml.rels",
        "ppt/notesSlides/notesSlide2.xml",
        "ppt/notesSlides/_rels/notesSlide2.xml.rels",
    }


def test_update_content_types(tmp_path: Path):
    ct_path = tmp_path / "[Content_Types].xml"
    ct_path.write_text(
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Override PartName="/ppt/slides/slide1.xml" ContentType="type1"/>'
        '<Override PartName="/ppt/slides/slide2.xml" ContentType="type2"/>'
        '</Types>'
    )

    update_content_types(tmp_path, ["ppt/slides/slide2.xml"])

    content = ct_path.read_text()
    assert "slide1.xml" in content
    assert "slide2.xml" not in content


def test_clean_unused_files(tmp_path: Path):
    ppt_dir = tmp_path / "ppt"
    slides_dir = ppt_dir / "slides"
    slides_rels_dir = slides_dir / "_rels"
    slides_rels_dir.mkdir(parents=True)

    pres_rels_dir = ppt_dir / "_rels"
    pres_rels_dir.mkdir(parents=True)

    pres_rels_path = pres_rels_dir / "presentation.xml.rels"
    pres_path = ppt_dir / "presentation.xml"

    pres_rels_path.write_text(
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide1.xml"/>'
        '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide2.xml"/>'
        '</Relationships>'
    )
    pres_path.write_text(
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        '<p:sldIdLst>'
        '<p:sldId id="256" r:id="rId1"/>'
        '</p:sldIdLst>'
        '</p:presentation>'
    )

    slide1 = slides_dir / "slide1.xml"
    slide2 = slides_dir / "slide2.xml"
    slide1.write_text("<test/>")
    slide2.write_text("<test/>")

    slide1_rels = slides_rels_dir / "slide1.xml.rels"
    slide2_rels = slides_rels_dir / "slide2.xml.rels"
    slide1_rels.write_text(
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="type1" Target="../media/image1.png"/>'
        '</Relationships>'
    )
    slide2_rels.write_text(
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="type1" Target="../media/image2.png"/>'
        '</Relationships>'
    )

    media_dir = ppt_dir / "media"
    media_dir.mkdir(parents=True)
    media1 = media_dir / "image1.png"
    media2 = media_dir / "image2.png"
    media1.write_text("test")
    media2.write_text("test")

    ct_path = tmp_path / "[Content_Types].xml"
    ct_path.write_text(
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Override PartName="/ppt/slides/slide1.xml" ContentType="type1"/>'
        '<Override PartName="/ppt/slides/slide2.xml" ContentType="type2"/>'
        '<Override PartName="/ppt/media/image1.png" ContentType="type3"/>'
        '<Override PartName="/ppt/media/image2.png" ContentType="type4"/>'
        '</Types>'
    )

    removed = clean_unused_files(tmp_path)

    assert slide1.exists()
    assert not slide2.exists()
    assert media1.exists()
    assert not media2.exists()

    content_types = ct_path.read_text()
    assert "slide1.xml" in content_types
    assert "slide2.xml" not in content_types
    assert "image1.png" in content_types
    assert "image2.png" not in content_types

    assert set(removed) == {
        "ppt/slides/slide2.xml",
        "ppt/slides/_rels/slide2.xml.rels",
        "ppt/media/image2.png"
    }


def test_empty_dirs(tmp_path: Path):
    assert get_slides_in_sldidlst(tmp_path) == set()
    assert remove_orphaned_slides(tmp_path) == []
    assert remove_trash_directory(tmp_path) == []
    assert get_slide_referenced_files(tmp_path) == set()
    assert remove_orphaned_rels_files(tmp_path) == []
    assert get_referenced_files(tmp_path) == set()
    assert remove_orphaned_files(tmp_path, set()) == []
    update_content_types(tmp_path, [])
    assert clean_unused_files(tmp_path) == []

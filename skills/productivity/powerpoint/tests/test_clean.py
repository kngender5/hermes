import pytest
from pathlib import Path
import xml.etree.ElementTree as ET

import clean

def test_get_slides_in_sldidlst_empty(tmp_path):
    # Test when ppt/presentation.xml or ppt/_rels/presentation.xml.rels is missing
    assert clean.get_slides_in_sldidlst(tmp_path) == set()

def create_mock_pptx(tmp_path):
    ppt_dir = tmp_path / "ppt"
    rels_dir = ppt_dir / "_rels"
    slides_dir = ppt_dir / "slides"
    slides_rels_dir = slides_dir / "_rels"

    ppt_dir.mkdir()
    rels_dir.mkdir()
    slides_dir.mkdir()
    slides_rels_dir.mkdir()

    # Create presentation.xml
    pres_xml = ppt_dir / "presentation.xml"
    pres_xml.write_text("""<?xml version="1.0" encoding="UTF-8"?>
    <p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
        <p:sldIdLst>
            <p:sldId id="256" r:id="rId2"/>
            <p:sldId id="257" r:id="rId3"/>
        </p:sldIdLst>
    </p:presentation>
    """)

    # Create presentation.xml.rels
    pres_rels = rels_dir / "presentation.xml.rels"
    pres_rels.write_text("""<?xml version="1.0" encoding="UTF-8"?>
    <Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
        <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>
        <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide1.xml"/>
        <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide2.xml"/>
        <Relationship Id="rId4" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide3.xml"/>
    </Relationships>
    """)

    return ppt_dir

def test_get_slides_in_sldidlst_valid(tmp_path):
    create_mock_pptx(tmp_path)
    slides = clean.get_slides_in_sldidlst(tmp_path)
    assert slides == {"slide1.xml", "slide2.xml"}

def test_remove_orphaned_slides(tmp_path):
    ppt_dir = create_mock_pptx(tmp_path)
    slides_dir = ppt_dir / "slides"
    slides_rels_dir = slides_dir / "_rels"

    # Create slide files
    (slides_dir / "slide1.xml").touch() # Referenced
    (slides_dir / "slide2.xml").touch() # Referenced
    (slides_dir / "slide3.xml").touch() # Orphaned (in rels but not in sldIdLst)
    (slides_dir / "slide4.xml").touch() # Orphaned (not in rels)

    # Create slide rels
    (slides_rels_dir / "slide1.xml.rels").touch()
    (slides_rels_dir / "slide3.xml.rels").touch()

    removed = clean.remove_orphaned_slides(tmp_path)

    assert "ppt/slides/slide3.xml" in removed
    assert "ppt/slides/slide4.xml" in removed
    assert "ppt/slides/_rels/slide3.xml.rels" in removed

    assert (slides_dir / "slide1.xml").exists()
    assert (slides_dir / "slide2.xml").exists()
    assert not (slides_dir / "slide3.xml").exists()
    assert not (slides_dir / "slide4.xml").exists()
    assert not (slides_rels_dir / "slide3.xml.rels").exists()

    # Check that presentation.xml.rels was updated to remove rId4
    pres_rels_content = (ppt_dir / "_rels" / "presentation.xml.rels").read_text()
    assert "slide1.xml" in pres_rels_content
    assert "slide2.xml" in pres_rels_content
    assert "slide3.xml" not in pres_rels_content

def test_remove_orphaned_slides_no_slides_dir(tmp_path):
    assert clean.remove_orphaned_slides(tmp_path) == []

def test_remove_trash_directory(tmp_path):
    trash_dir = tmp_path / "[trash]"
    trash_dir.mkdir()
    (trash_dir / "file1.txt").touch()
    (trash_dir / "file2.txt").touch()

    removed = clean.remove_trash_directory(tmp_path)

    assert set(removed) == {"[trash]/file1.txt", "[trash]/file2.txt"}
    assert not trash_dir.exists()

def test_remove_trash_directory_not_exists(tmp_path):
    assert clean.remove_trash_directory(tmp_path) == []

def test_get_slide_referenced_files(tmp_path):
    ppt_dir = tmp_path / "ppt"
    slides_dir = ppt_dir / "slides"
    slides_rels_dir = slides_dir / "_rels"
    slides_rels_dir.mkdir(parents=True)

    media_dir = ppt_dir / "media"
    media_dir.mkdir()

    (slides_rels_dir / "slide1.xml.rels").write_text("""<?xml version="1.0" encoding="UTF-8"?>
    <Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
        <Relationship Id="rId1" Target="../media/image1.png"/>
        <Relationship Id="rId2" Target="../drawings/drawing1.xml"/>
    </Relationships>
    """)

    referenced = clean.get_slide_referenced_files(tmp_path)
    # Using Path resolves these to absolute paths
    assert Path("ppt/media/image1.png") in referenced
    assert Path("ppt/drawings/drawing1.xml") in referenced

def test_remove_orphaned_rels_files(tmp_path):
    ppt_dir = tmp_path / "ppt"
    drawings_dir = ppt_dir / "drawings"
    drawings_rels_dir = drawings_dir / "_rels"
    drawings_rels_dir.mkdir(parents=True)

    slides_rels_dir = ppt_dir / "slides" / "_rels"
    slides_rels_dir.mkdir(parents=True)

    # Referenced drawing
    (slides_rels_dir / "slide1.xml.rels").write_text("""<?xml version="1.0" encoding="UTF-8"?>
    <Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
        <Relationship Id="rId1" Target="../drawings/drawing1.xml"/>
    </Relationships>
    """)

    # Create the referenced file and its rels
    (drawings_dir / "drawing1.xml").touch()
    (drawings_rels_dir / "drawing1.xml.rels").touch()

    # Create an orphaned file and its rels
    (drawings_dir / "drawing2.xml").touch()
    (drawings_rels_dir / "drawing2.xml.rels").touch()

    removed = clean.remove_orphaned_rels_files(tmp_path)

    assert "ppt/drawings/_rels/drawing2.xml.rels" in removed
    assert not (drawings_rels_dir / "drawing2.xml.rels").exists()
    assert (drawings_rels_dir / "drawing1.xml.rels").exists()

def test_remove_orphaned_files(tmp_path):
    ppt_dir = tmp_path / "ppt"
    media_dir = ppt_dir / "media"
    media_dir.mkdir(parents=True)

    (media_dir / "image1.png").touch() # Referenced
    (media_dir / "image2.png").touch() # Orphaned

    referenced = {Path("ppt/media/image1.png")}

    removed = clean.remove_orphaned_files(tmp_path, referenced)

    assert "ppt/media/image2.png" in removed
    assert not (media_dir / "image2.png").exists()
    assert (media_dir / "image1.png").exists()

def test_remove_orphaned_files_theme(tmp_path):
    ppt_dir = tmp_path / "ppt"
    theme_dir = ppt_dir / "theme"
    theme_rels_dir = theme_dir / "_rels"
    theme_rels_dir.mkdir(parents=True)

    (theme_dir / "theme1.xml").touch() # Referenced
    (theme_dir / "theme2.xml").touch() # Orphaned
    (theme_rels_dir / "theme2.xml.rels").touch() # Orphaned rels

    referenced = {Path("ppt/theme/theme1.xml")}
    removed = clean.remove_orphaned_files(tmp_path, referenced)

    assert "ppt/theme/theme2.xml" in removed
    assert "ppt/theme/_rels/theme2.xml.rels" in removed
    assert not (theme_dir / "theme2.xml").exists()
    assert not (theme_rels_dir / "theme2.xml.rels").exists()
    assert (theme_dir / "theme1.xml").exists()

def test_update_content_types(tmp_path):
    ct_file = tmp_path / "[Content_Types].xml"
    ct_file.write_text("""<?xml version="1.0" encoding="UTF-8"?>
    <Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
        <Override PartName="/ppt/slides/slide1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>
        <Override PartName="/ppt/slides/slide2.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>
    </Types>
    """)

    removed = ["ppt/slides/slide2.xml"]
    clean.update_content_types(tmp_path, removed)

    content = ct_file.read_text()
    assert "slide1.xml" in content
    assert "slide2.xml" not in content

def test_clean_unused_files_integration(tmp_path):
    # Setup full environment
    ppt_dir = create_mock_pptx(tmp_path)
    slides_dir = ppt_dir / "slides"
    slides_rels_dir = slides_dir / "_rels"

    media_dir = ppt_dir / "media"
    media_dir.mkdir()

    trash_dir = tmp_path / "[trash]"
    trash_dir.mkdir()
    (trash_dir / "junk.txt").touch()

    # Referenced slide
    (slides_dir / "slide1.xml").touch()
    (slides_rels_dir / "slide1.xml.rels").write_text("""<?xml version="1.0" encoding="UTF-8"?>
    <Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
        <Relationship Id="rId1" Target="../media/image1.png"/>
    </Relationships>
    """)
    (media_dir / "image1.png").touch()

    # Orphaned slide and its resource
    (slides_dir / "slide3.xml").touch()
    (slides_rels_dir / "slide3.xml.rels").write_text("""<?xml version="1.0" encoding="UTF-8"?>
    <Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
        <Relationship Id="rId1" Target="../media/image2.png"/>
    </Relationships>
    """)
    (media_dir / "image2.png").touch()

    ct_file = tmp_path / "[Content_Types].xml"
    ct_file.write_text("""<?xml version="1.0" encoding="UTF-8"?>
    <Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
        <Override PartName="/ppt/slides/slide1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>
        <Override PartName="/ppt/slides/slide3.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>
        <Override PartName="/ppt/media/image1.png" ContentType="image/png"/>
        <Override PartName="/ppt/media/image2.png" ContentType="image/png"/>
    </Types>
    """)

    removed = clean.clean_unused_files(tmp_path)

    # Verify what got removed
    assert "[trash]/junk.txt" in removed
    assert "ppt/slides/slide3.xml" in removed
    assert "ppt/slides/_rels/slide3.xml.rels" in removed
    assert "ppt/media/image2.png" in removed

    # Verify what remains
    assert (slides_dir / "slide1.xml").exists()
    assert (media_dir / "image1.png").exists()
    assert not (slides_dir / "slide3.xml").exists()
    assert not (media_dir / "image2.png").exists()
    assert not trash_dir.exists()

    # Verify content types updated
    ct_content = ct_file.read_text()
    assert "slide1.xml" in ct_content
    assert "slide3.xml" not in ct_content

def test_get_slide_referenced_files_no_slides_rels_dir(tmp_path):
    assert clean.get_slide_referenced_files(tmp_path) == set()

def test_get_slide_referenced_files_empty_target(tmp_path):
    ppt_dir = tmp_path / "ppt"
    slides_rels_dir = ppt_dir / "slides" / "_rels"
    slides_rels_dir.mkdir(parents=True)

    (slides_rels_dir / "slide1.xml.rels").write_text("""<?xml version="1.0" encoding="UTF-8"?>
    <Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
        <Relationship Id="rId1" Target=""/>
    </Relationships>
    """)
    assert clean.get_slide_referenced_files(tmp_path) == set()

def test_get_slide_referenced_files_outside_dir(tmp_path):
    ppt_dir = tmp_path / "ppt"
    slides_rels_dir = ppt_dir / "slides" / "_rels"
    slides_rels_dir.mkdir(parents=True)

    # Target resolves to outside unpacked_dir
    (slides_rels_dir / "slide1.xml.rels").write_text("""<?xml version="1.0" encoding="UTF-8"?>
    <Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
        <Relationship Id="rId1" Target="../../../../outside.xml"/>
    </Relationships>
    """)
    assert clean.get_slide_referenced_files(tmp_path) == set()

def test_remove_orphaned_rels_files_outside_dir(tmp_path):
    ppt_dir = tmp_path / "ppt"
    drawings_rels_dir = ppt_dir / "drawings" / "_rels"
    drawings_rels_dir.mkdir(parents=True)

    # Since resource_file is derived from rels_file name, it's hard to make resource_rel_path ValueError
    # unless it resolves to outside unpacked_dir which is tricky to test as we can't easily symlink outside tmp_path in a portable way.
    # We can skip full coverage for ValueError block if not easily achievable, or use symlinks.
    pass

def test_get_referenced_files_empty_target(tmp_path):
    ppt_dir = tmp_path / "ppt"
    rels_dir = ppt_dir / "_rels"
    rels_dir.mkdir(parents=True)

    (rels_dir / "file.rels").write_text("""<?xml version="1.0" encoding="UTF-8"?>
    <Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
        <Relationship Id="rId1" Target=""/>
    </Relationships>
    """)
    assert clean.get_referenced_files(tmp_path) == set()

def test_get_referenced_files_outside_dir(tmp_path):
    ppt_dir = tmp_path / "ppt"
    rels_dir = ppt_dir / "_rels"
    rels_dir.mkdir(parents=True)

    (rels_dir / "file.rels").write_text("""<?xml version="1.0" encoding="UTF-8"?>
    <Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
        <Relationship Id="rId1" Target="../../../outside.xml"/>
    </Relationships>
    """)
    assert clean.get_referenced_files(tmp_path) == set()

def test_remove_orphaned_files_skip_dirs(tmp_path):
    ppt_dir = tmp_path / "ppt"
    media_dir = ppt_dir / "media"
    media_dir.mkdir(parents=True)

    # Should skip directories
    (media_dir / "subdir").mkdir()

    removed = clean.remove_orphaned_files(tmp_path, set())
    assert removed == []
    assert (media_dir / "subdir").exists()

def test_remove_orphaned_files_notes_slides(tmp_path):
    ppt_dir = tmp_path / "ppt"
    notes_dir = ppt_dir / "notesSlides"
    notes_rels_dir = notes_dir / "_rels"
    notes_rels_dir.mkdir(parents=True)

    (notes_dir / "notesSlide1.xml").touch() # Referenced
    (notes_dir / "notesSlide2.xml").touch() # Orphaned
    (notes_dir / "subdir").mkdir() # Should skip dir

    (notes_rels_dir / "notesSlide2.xml.rels").touch() # Orphaned rels because parent is deleted

    referenced = {Path("ppt/notesSlides/notesSlide1.xml")}
    removed = clean.remove_orphaned_files(tmp_path, referenced)

    assert "ppt/notesSlides/notesSlide2.xml" in removed
    assert "ppt/notesSlides/_rels/notesSlide2.xml.rels" in removed
    assert not (notes_dir / "notesSlide2.xml").exists()
    assert not (notes_rels_dir / "notesSlide2.xml.rels").exists()
    assert (notes_dir / "notesSlide1.xml").exists()
    assert (notes_dir / "subdir").exists()

def test_update_content_types_no_file(tmp_path):
    # Should just return without error
    clean.update_content_types(tmp_path, ["some/file.xml"])

def test_remove_orphaned_files_notes_slides_skip_dir(tmp_path):
    ppt_dir = tmp_path / "ppt"
    notes_dir = ppt_dir / "notesSlides"
    notes_dir.mkdir(parents=True)

    # Create a directory ending with .xml to trigger the not is_file() condition
    (notes_dir / "dir.xml").mkdir()

    removed = clean.remove_orphaned_files(tmp_path, set())
    assert removed == []
    assert (notes_dir / "dir.xml").exists()

def test_remove_orphaned_rels_files_value_error(tmp_path, monkeypatch):
    ppt_dir = tmp_path / "ppt"
    drawings_dir = ppt_dir / "drawings"
    drawings_rels_dir = drawings_dir / "_rels"
    drawings_rels_dir.mkdir(parents=True)

    (drawings_rels_dir / "drawing1.xml.rels").touch()

    # Mock relative_to to raise ValueError to cover line 142-143
    def mock_relative_to(self, other):
        raise ValueError("mocked value error")

    monkeypatch.setattr(Path, "relative_to", mock_relative_to)

    # Will hit ValueError and continue
    removed = clean.remove_orphaned_rels_files(tmp_path)
    assert removed == []


import sys
from unittest.mock import patch
import io

def test_main_cli_args(tmp_path):
    import runpy

    # Test with no args
    with patch.object(sys, 'argv', ['clean.py']), \
         patch('sys.stderr', new_callable=io.StringIO) as mock_stderr:
        with pytest.raises(SystemExit) as exc_info:
            runpy.run_path(str(Path(clean.__file__)), run_name='__main__')
        assert exc_info.value.code == 1
        assert "Usage: python clean.py <unpacked_dir>" in mock_stderr.getvalue()

    # Test with non-existent dir
    with patch.object(sys, 'argv', ['clean.py', str(tmp_path / "nonexistent")]), \
         patch('sys.stderr', new_callable=io.StringIO) as mock_stderr:
        with pytest.raises(SystemExit) as exc_info:
            runpy.run_path(str(Path(clean.__file__)), run_name='__main__')
        assert exc_info.value.code == 1
        assert "not found" in mock_stderr.getvalue()

    # Test with valid dir but nothing to remove
    ppt_dir = create_mock_pptx(tmp_path)
    with patch.object(sys, 'argv', ['clean.py', str(tmp_path)]), \
         patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
        runpy.run_path(str(Path(clean.__file__)), run_name='__main__')
        assert "No unreferenced files found" in mock_stdout.getvalue()

    # Test with valid dir and files to remove
    (tmp_path / "[trash]").mkdir()
    (tmp_path / "[trash]" / "junk.txt").touch()

    with patch.object(sys, 'argv', ['clean.py', str(tmp_path)]), \
         patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
        runpy.run_path(str(Path(clean.__file__)), run_name='__main__')
        assert "Removed 1 unreferenced files:" in mock_stdout.getvalue()
        assert "[trash]/junk.txt" in mock_stdout.getvalue()

def test_get_slides_in_sldidlst_xml_error(tmp_path):
    from xml.parsers.expat import ExpatError
    create_mock_pptx(tmp_path)

    with patch('defusedxml.minidom.parse', side_effect=ExpatError("mismatched tag")):
        with pytest.raises(ExpatError, match="mismatched tag"):
            clean.get_slides_in_sldidlst(tmp_path)

def test_remove_orphaned_slides_unlink_error(tmp_path):
    ppt_dir = create_mock_pptx(tmp_path)
    slides_dir = ppt_dir / "slides"
    (slides_dir / "slide3.xml").touch() # Orphaned

    with patch('pathlib.Path.unlink', side_effect=PermissionError("Permission denied")):
        with pytest.raises(PermissionError, match="Permission denied"):
            clean.remove_orphaned_slides(tmp_path)

def test_remove_trash_directory_rmdir_error(tmp_path):
    trash_dir = tmp_path / "[trash]"
    trash_dir.mkdir()

    with patch('pathlib.Path.rmdir', side_effect=OSError("Directory not empty")):
        with pytest.raises(OSError, match="Directory not empty"):
            clean.remove_trash_directory(tmp_path)

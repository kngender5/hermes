import pytest
from pathlib import Path
from xml.dom import minidom
from skills.productivity.powerpoint.scripts.office.helpers.merge_runs import merge_runs

def create_mock_doc(tmp_path: Path, xml_content: str) -> Path:
    """Helper to create a mocked document.xml with standard structure"""
    doc_dir = tmp_path / "word"
    doc_dir.mkdir(parents=True)
    doc_xml = doc_dir / "document.xml"

    full_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
    <w:body>
        {xml_content}
    </w:body>
</w:document>"""
    doc_xml.write_text(full_xml, encoding="utf-8")
    return tmp_path

def test_missing_document(tmp_path):
    count, msg = merge_runs(str(tmp_path))
    assert count == 0
    assert "not found" in msg

def test_malformed_xml(tmp_path):
    doc_dir = tmp_path / "word"
    doc_dir.mkdir(parents=True)
    doc_xml = doc_dir / "document.xml"
    doc_xml.write_text("<w:document><w:body>unclosed tag</w:body>", encoding="utf-8")

    count, msg = merge_runs(str(tmp_path))
    assert count == 0
    assert "Error:" in msg

def test_merge_adjacent_runs_no_rpr(tmp_path):
    xml = """
    <w:p>
        <w:r><w:t>Hello </w:t></w:r>
        <w:r><w:t>World</w:t></w:r>
    </w:p>
    """
    input_dir = create_mock_doc(tmp_path, xml)

    count, msg = merge_runs(str(input_dir))
    assert count == 1

    doc_xml = input_dir / "word" / "document.xml"
    dom = minidom.parseString(doc_xml.read_text(encoding="utf-8"))
    runs = dom.getElementsByTagName("w:r")
    assert len(runs) == 1
    texts = dom.getElementsByTagName("w:t")
    assert len(texts) == 1
    assert texts[0].firstChild.nodeValue == "Hello World"
    assert texts[0].getAttribute("xml:space") != "preserve"

def test_merge_adjacent_runs_same_rpr(tmp_path):
    xml = """
    <w:p>
        <w:r>
            <w:rPr><w:b/></w:rPr>
            <w:t>Bold </w:t>
        </w:r>
        <w:r>
            <w:rPr><w:b/></w:rPr>
            <w:t>Text</w:t>
        </w:r>
    </w:p>
    """
    input_dir = create_mock_doc(tmp_path, xml)

    count, msg = merge_runs(str(input_dir))
    assert count == 1

    doc_xml = input_dir / "word" / "document.xml"
    dom = minidom.parseString(doc_xml.read_text(encoding="utf-8"))
    runs = dom.getElementsByTagName("w:r")
    assert len(runs) == 1

    rprs = runs[0].getElementsByTagName("w:rPr")
    assert len(rprs) == 1

    texts = dom.getElementsByTagName("w:t")
    assert len(texts) == 1
    assert texts[0].firstChild.nodeValue == "Bold Text"
    assert texts[0].getAttribute("xml:space") != "preserve"

def test_dont_merge_different_rpr(tmp_path):
    xml = """
    <w:p>
        <w:r>
            <w:rPr><w:b/></w:rPr>
            <w:t>Bold </w:t>
        </w:r>
        <w:r>
            <w:rPr><w:i/></w:rPr>
            <w:t>Italic</w:t>
        </w:r>
    </w:p>
    """
    input_dir = create_mock_doc(tmp_path, xml)

    count, msg = merge_runs(str(input_dir))
    assert count == 0

    doc_xml = input_dir / "word" / "document.xml"
    dom = minidom.parseString(doc_xml.read_text(encoding="utf-8"))
    runs = dom.getElementsByTagName("w:r")
    assert len(runs) == 2

def test_remove_prooferr_and_rsid(tmp_path):
    xml = """
    <w:p>
        <w:proofErr w:type="spellStart"/>
        <w:r w:rsidR="00000000"><w:t>Spell</w:t></w:r>
        <w:proofErr w:type="spellEnd"/>
        <w:r w:rsidR="00000000"><w:t>Check</w:t></w:r>
    </w:p>
    """
    input_dir = create_mock_doc(tmp_path, xml)

    count, msg = merge_runs(str(input_dir))
    assert count == 1

    doc_xml = input_dir / "word" / "document.xml"
    dom = minidom.parseString(doc_xml.read_text(encoding="utf-8"))

    proofs = dom.getElementsByTagName("w:proofErr")
    assert len(proofs) == 0

    runs = dom.getElementsByTagName("w:r")
    assert len(runs) == 1
    assert not runs[0].hasAttribute("w:rsidR")

def test_merge_multiple_t_elements_in_run(tmp_path):
    xml = """
    <w:p>
        <w:r>
            <w:t>One </w:t>
            <w:t>Two </w:t>
        </w:r>
        <w:r>
            <w:t>Three</w:t>
        </w:r>
    </w:p>
    """
    input_dir = create_mock_doc(tmp_path, xml)

    count, msg = merge_runs(str(input_dir))
    assert count == 1

    doc_xml = input_dir / "word" / "document.xml"
    dom = minidom.parseString(doc_xml.read_text(encoding="utf-8"))
    runs = dom.getElementsByTagName("w:r")
    assert len(runs) == 1

    texts = dom.getElementsByTagName("w:t")
    assert len(texts) == 1
    assert texts[0].firstChild.nodeValue == "One Two Three"
    assert texts[0].getAttribute("xml:space") != "preserve"

def test_xml_space_preserve(tmp_path):
    xml = """
    <w:p>
        <w:r><w:t>Hello</w:t></w:r>
        <w:r><w:t xml:space="preserve"> World </w:t></w:r>
    </w:p>
    """
    input_dir = create_mock_doc(tmp_path, xml)

    count, msg = merge_runs(str(input_dir))
    assert count == 1

    doc_xml = input_dir / "word" / "document.xml"
    dom = minidom.parseString(doc_xml.read_text(encoding="utf-8"))
    texts = dom.getElementsByTagName("w:t")
    assert len(texts) == 1
    assert texts[0].firstChild.nodeValue == "Hello World "
    # Should get preserved because of trailing/leading spaces
    assert texts[0].getAttribute("xml:space") == "preserve"

def test_complex_merge(tmp_path):
    xml = """
    <w:p>
        <w:r><w:t>A</w:t></w:r>
        <w:r><w:t>B</w:t></w:r>
        <w:r>
            <w:rPr><w:b/></w:rPr>
            <w:t>C</w:t>
        </w:r>
        <w:r>
            <w:rPr><w:b/></w:rPr>
            <w:t>D</w:t>
        </w:r>
        <w:r><w:t>E</w:t></w:r>
    </w:p>
    """
    input_dir = create_mock_doc(tmp_path, xml)

    count, msg = merge_runs(str(input_dir))
    assert count == 2 # Merges A+B and C+D

    doc_xml = input_dir / "word" / "document.xml"
    dom = minidom.parseString(doc_xml.read_text(encoding="utf-8"))
    runs = dom.getElementsByTagName("w:r")
    assert len(runs) == 3

    texts = dom.getElementsByTagName("w:t")
    assert len(texts) == 3
    assert texts[0].firstChild.nodeValue == "AB"
    assert texts[1].firstChild.nodeValue == "CD"
    assert texts[2].firstChild.nodeValue == "E"

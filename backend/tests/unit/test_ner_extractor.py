"""NER extractor unit tests."""

from app.ingestion.ner_extractor import ner_extractor


def test_extract_entities_empty() -> None:
    assert ner_extractor.extract_entities("") == []
    assert ner_extractor.extract_entities(None) == []


def test_extract_entities_english() -> None:
    text = "Google was founded by Larry Page and Sergey Brin in California."
    entities = ner_extractor.extract_entities(text, language="en")

    names = {ent["name"] for ent in entities}

    assert len(entities) > 0
    assert any("Google" in name for name in names)
    assert any("Larry Page" in name for name in names)


def test_extract_entities_german() -> None:
    text = "Die Allianz SE hat ihren Hauptsitz in München."
    entities = ner_extractor.extract_entities(text, language="de")

    names = {ent["name"] for ent in entities}

    assert len(entities) > 0
    assert any("Allianz" in name for name in names)
    assert any("München" in name for name in names)

"""Node labels, relationship types, constraints."""

from enum import StrEnum


class NodeLabel(StrEnum):
    DOCUMENT = "Document"
    CHUNK = "Chunk"
    ENTITY = "Entity"
    LEGAL_ARTICLE = "LegalArticle"
    ORGANISATION = "Organisation"
    PERSON = "Person"
    CONCEPT = "Concept"


class RelType(StrEnum):
    HAS_CHUNK = "HAS_CHUNK"
    MENTIONS = "MENTIONS"
    CITES = "CITES"
    AMENDS = "AMENDS"
    REFERS_TO = "REFERS_TO"
    PART_OF = "PART_OF"
    SUBJECT_OF = "SUBJECT_OF"
    RELATED_TO = "RELATED_TO"
    TRANSLATED_FROM = "TRANSLATED_FROM"

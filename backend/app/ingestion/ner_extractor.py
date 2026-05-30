"""spaCy multilingual NER."""

import spacy
import structlog
from typing import Any

logger = structlog.get_logger(__name__)

class NERExtractor:
    def __init__(self) -> None:
        try:
            self.nlp_multi = spacy.load("xx_ent_wiki_sm")
            self.nlp_de = spacy.load("de_core_news_sm")
        except OSError as e:
            logger.warning(f"Failed to load spaCy models, please run 'python -m spacy download xx_ent_wiki_sm'. Error: {e}")
            self.nlp_multi = None
            self.nlp_de = None

    def extract_entities(self, text: str, language: str = "en") -> list[dict[str, Any]]:
        """Extracts ORG, PER, LOC, MISC entities from text."""
        if not text:
            return []
            
        nlp = self.nlp_de if language == "de" and self.nlp_de else self.nlp_multi
        if not nlp:
            return []

        # Increase max_length for long documents if needed, but we expect chunked text here
        doc = nlp(text)
        entities = []
        seen = set()
        for ent in doc.ents:
            ent_type = ent.label_
            if ent_type in ("ORG", "PER", "LOC", "MISC", "LAW"):
                key = f"{ent.text}_{ent_type}"
                if key not in seen:
                    entities.append({
                        "name": ent.text,
                        "type": ent_type
                    })
                    seen.add(key)
        return entities

ner_extractor = NERExtractor()

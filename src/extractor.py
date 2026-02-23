import spacy
import re
from typing import Dict, List, Optional

EDU_KEYWORDS = [
    "education", "qualifications", "academic", "degree", "bachelor", "master",
    "phd", "university", "college", "coursework"
]
EXP_KEYWORDS = [
    "experience", "employment", "work history", "professional experience",
    "projects", "roles", "responsibilities"
]
SKILL_KEYWORDS = [
    "skills", "technical skills", "key skills", "core competencies",
    "tools", "technologies"
]

class ResumeExtractor:
    def __init__(self, model: str = "en_core_web_sm"):
        self.nlp = spacy.load(model)

    def _section_extract(self, text: str, keywords: List[str]) -> Optional[str]:
        # Simple section splitter by keyword headers
        lower = text.lower()
        indices = []
        for kw in keywords:
            idx = lower.find(kw)
            if idx != -1:
                indices.append(idx)
        if not indices:
            return None
        start = min(indices)
        # Find next header-like boundary
        # naive: next occurrence of two newlines or another keyword
        end = len(text)
        for kw in (EDU_KEYWORDS + EXP_KEYWORDS + SKILL_KEYWORDS):
            if kw in lower[start+1:]:
                candidate = lower.find(kw, start+1)
                if candidate != -1:
                    end = min(end, candidate)
        return text[start:end].strip()

    def extract(self, text: str) -> Dict:
        doc = self.nlp(text)

        # Named entities for organizations, degrees, etc.
        orgs = [ent.text for ent in doc.ents if ent.label_ in ("ORG", "FAC")]
        dates = [ent.text for ent in doc.ents if ent.label_ in ("DATE",)]
        persons = [ent.text for ent in doc.ents if ent.label_ in ("PERSON",)]

        education = self._section_extract(text, EDU_KEYWORDS)
        experience = self._section_extract(text, EXP_KEYWORDS)
        skills = self._section_extract(text, SKILL_KEYWORDS)

        return {
            "persons": persons,
            "orgs": orgs,
            "dates": dates,
            "education": education,
            "experience": experience,
            "skills": skills,
        }

from typing import Dict

def compute_feature_bonus(resume_fields: Dict, jd_text: str) -> float:
    # Optional: add small bonuses for explicit matches (e.g., certifications)
    bonus = 0.0
    skills = (resume_fields.get("skills") or "").lower()
    jd_lower = jd_text.lower()

    # Example bonuses
    for kw, weight in [
        ("python", 0.03),
        ("machine learning", 0.04),
        ("nlp", 0.03),
        ("flask", 0.02),
        ("streamlit", 0.02),
        ("docker", 0.02),
        ("aws", 0.03),
    ]:
        if kw in skills and kw in jd_lower:
            bonus += weight

    return min(bonus, 0.1)  # cap bonus

def aggregate_score(base_score: float, bonus: float) -> float:
    return min(base_score + bonus, 1.0)

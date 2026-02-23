import numpy as np             
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rapidfuzz import fuzz                

# Initialize vectorizer globally
vectorizer = TfidfVectorizer()

# -----------------------------   
# TF-IDF Cosine Similarity
# -----------------------------
def tfidf_cosine(resume_text: str, jd_text: str) -> float:
    """
    Compute cosine similarity between resume and job description using TF-IDF.   
    Returns a score between 0 and 1.  
    """
    vectorizer.fit([resume_text, jd_text])       

    resume_vec = vectorizer.transform([resume_text]).toarray()     
    jd_vec = vectorizer.transform([jd_text]).toarray()

    sim = cosine_similarity(jd_vec, resume_vec)
    return float(sim[0][0])


# -----------------------------
# Fuzzy String Similarity
# -----------------------------
def fuzzy_similarity(resume_text: str, jd_text: str) -> float:
    """
    Compute fuzzy string similarity using token set ratio.
    Returns a score between 0 and 1.
    """
    return fuzz.token_set_ratio(resume_text, jd_text) / 100.0


# -----------------------------
# Keyword Bonus Scoring           
# -----------------------------
def keyword_bonus(resume_text: str, jd_text: str) -> float:
    """
    Award bonus points for presence of important keywords.
    Returns a score between 0 and 1.
    """
    keywords = ["Python", "Java", "SQL", "Machine Learning", "Streamlit", "NLP"]
    bonus = 0
    for kw in keywords:
        if kw.lower() in resume_text.lower() and kw.lower() in jd_text.lower():
            bonus += 1
    # Normalize bonus (max = number of keywords)
    return bonus / len(keywords)


# -----------------------------
# Aggregate Scoring
# -----------------------------
def match_resume(resume_sections, jd_text: str) -> dict:
    """
    Aggregate similarity scores between resume and job description.
    Returns a dictionary with tfidf, fuzzy, keyword, and final scores.
    """
    # Convert dict to string if needed
    if isinstance(resume_sections, dict):
        resume_text = " ".join(str(v) for v in resume_sections.values())
    else:
        resume_text = str(resume_sections)

    tfidf_score = tfidf_cosine(resume_text, jd_text)
    fuzzy_score = fuzzy_similarity(resume_text, jd_text)
    keyword_score = keyword_bonus(resume_text, jd_text)

    # Weighted final score (you can adjust weights)
    final_score = (0.5 * tfidf_score) + (0.3 * fuzzy_score) + (0.2 * keyword_score)

    return {
        "tfidf_score": tfidf_score,
        "fuzzy_similarity": fuzzy_score,
        "keyword_score": keyword_score,
        "final_score": final_score
    }
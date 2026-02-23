import streamlit as st
import pandas as pd
from pathlib import Path

from src.utils import clean_text, is_pdf, is_docx
from src.parser_pdf import parse_pdf
from src.parser_docx import parse_docx
from src.extractor import ResumeExtractor
from src.matcher import match_resume
from src.scoring import compute_feature_bonus, aggregate_score
from src.normalizer import normalize_email, normalize_phone, normalize_name

st.set_page_config(page_title="Resume Screening", page_icon="🧭", layout="wide")

st.title("🧭 Resume Screening App")
st.caption("Upload multiple resumes (PDF/DOCX/TXT), paste a job description, and get ranked results.")

# Sidebar: Job description
st.sidebar.header("Job description")
jd_text = st.sidebar.text_area(
    "Paste the job description here",
    height=300,
    placeholder="Role summary, responsibilities, required skills, qualifications..."
)

# File uploader
uploaded_files = st.file_uploader(
    "Upload resumes (PDF, DOCX, or TXT)",
    type=["pdf", "docx", "txt"],
    accept_multiple_files=True
)

# Options
st.sidebar.header("Options")
model_name = st.sidebar.selectbox("spaCy model", ["en_core_web_sm"], index=0)
show_details = st.sidebar.checkbox("Show extracted details", value=False)

if st.button("Run screening", type="primary"):
    if not jd_text.strip():
        st.warning("Please paste a job description.")
    elif not uploaded_files:
        st.warning("Please upload at least one resume.")
    else:
        extractor = ResumeExtractor(model=model_name)
        results = []

        with st.spinner("Processing resumes..."):
            for f in uploaded_files:
                filename = f.name
                bytes_data = f.read()

                # Unified parsing
                if is_pdf(filename):
                    raw_text = parse_pdf(bytes_data)
                elif is_docx(filename):
                    raw_text = parse_docx(bytes_data)
                elif filename.lower().endswith(".txt"):
                    raw_text = bytes_data.decode("utf-8", errors="ignore")
                else:
                    raw_text = ""

                raw_text = clean_text(raw_text)

                # Debug preview
                if not raw_text.strip():
                    st.warning(f"⚠️ Could not parse {filename}. Try saving/exporting as a text-based PDF or DOCX.")
                else:
                    st.text(f"Preview of {filename}:\n{raw_text[:300]}")

                # Extract fields
                fields = extractor.extract(raw_text)

                # Match & score
                base_scores = match_resume(fields, jd_text)
                bonus = compute_feature_bonus(fields, jd_text)
                final = aggregate_score(base_scores["final_score"], bonus)

                # Heuristic contact info
                email = normalize_email(raw_text)
                phone = normalize_phone(raw_text)
                name = normalize_name(raw_text) or (fields.get("persons")[0] if fields.get("persons") else None)

                results.append({
                    "Filename": filename,
                    "Name": name,
                    "Email": email,
                    "Phone": phone,
                    "TF-IDF": round(base_scores["tfidf_score"], 3),
                    "Fuzzy": round(base_scores["fuzzy_similarity"], 3),
                    "Bonus": round(bonus, 3),
                    "Final score": round(final, 3),
                    "Fields": fields,
                })

        # Rank and display
        df = pd.DataFrame(results).sort_values(by="Final score", ascending=False)
        st.subheader("Ranked candidates")
        st.dataframe(
            df[["Filename", "Name", "Email", "Phone", "TF-IDF", "Fuzzy", "Bonus", "Final score"]],
            use_container_width=True
        )

        if show_details:
            st.subheader("Extracted details")
            for row in df.to_dict(orient="records"):
                with st.expander(f"Details: {row['Filename']}"):
                    st.markdown(f"**Name:** {row['Name'] or 'N/A'}")
                    st.markdown(f"**Email:** {row['Email'] or 'N/A'}")
                    st.markdown(f"**Phone:** {row['Phone'] or 'N/A'}")
                    fields = row["Fields"]
                    st.markdown("**Education:**")
                    st.write(fields.get("education") or "N/A")
                    st.markdown("**Experience:**")
                    st.write(fields.get("experience") or "N/A")
                    st.markdown("**Skills:**")
                    st.write(fields.get("skills") or "N/A")
                    st.markdown("**Entities (ORG/PERSON/DATE):**")
                    st.write({
                        "persons": fields.get("persons"),
                        "orgs": fields.get("orgs"),
                        "dates": fields.get("dates"),
                    })

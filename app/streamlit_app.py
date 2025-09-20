import streamlit as st
import os
from src import parsing, scoring, embeddings, db

st.set_page_config(page_title="Resume Relevance Checker", layout="wide")
st.title("Automated Resume Relevance Check System")

# Upload JD
jd_file = st.file_uploader("Upload Job Description (txt/docx/pdf)", type=["txt","pdf","docx"])
# Upload Resume
resume_file = st.file_uploader("Upload Resume (txt/docx/pdf)", type=["txt","pdf","docx"])

if st.button("Evaluate Resume"):
    if jd_file and resume_file:
        # Extract text
        jd_text = parsing.extract_text(jd_file)
        resume_text = parsing.extract_text(resume_file)

        # Hard + semantic scoring
        score, verdict, matched, missing, suggestions = scoring.evaluate(resume_text, jd_text)

        st.metric("Relevance Score", f"{score}/100")
        st.write(f"Verdict: **{verdict}**")
        st.write("Matched Skills:", matched)
        st.write("Missing Skills:", missing)
        st.write("Suggestions:", suggestions)

        # Save result
        record = {
            "resume_name": resume_file.name,
            "jd_name": jd_file.name,
            "score": score,
            "verdict": verdict,
            "matched_skills": matched,
            "missing_skills": missing,
            "suggestions": suggestions
        }
        db.save_evaluation("data/evaluations.db", record)

import streamlit as st
from src import parsing, scoring, db

st.set_page_config(page_title="Resume Relevance Checker", layout="wide")
st.title("📄 Automated Resume Relevance Checker")

# Upload JD
jd_file = st.file_uploader("Upload Job Description (txt/pdf/docx)", type=["txt","pdf","docx"])
# Upload Resume
resume_file = st.file_uploader("Upload Resume (txt/pdf/docx)", type=["txt","pdf","docx"])

if st.button("Evaluate Resume"):
    if jd_file and resume_file:
        # Extract text
        jd_text = parsing.extract_text(jd_file)
        resume_text = parsing.extract_text(resume_file)

        # Scoring
        score, verdict, matched, missing, suggestions = scoring.evaluate(resume_text, jd_text)

        # Display results cleanly
        st.markdown(f"**Relevance Score:** {score}/100")
        st.markdown(f"**Verdict:** {verdict}")
        st.markdown(f"**Matched Skills:** {', '.join(matched) if matched else 'None'}")
        st.markdown(f"**Missing Skills:** {', '.join(missing) if missing else 'None'}")
        st.markdown(f"**Suggestions:** {', '.join(suggestions) if suggestions else 'None'}")

        # Save evaluation
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

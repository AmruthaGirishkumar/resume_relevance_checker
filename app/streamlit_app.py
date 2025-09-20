import streamlit as st
from src import parsing, scoring

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

        # Evaluate
        result = scoring.evaluate(resume_text, jd_text)

        # Display results
        st.metric("Relevance Score", f"{result['score']:.1f}/100")  
        st.write(f"Verdict: **{result['verdict']}**")
        st.write(f"Matched Skills: {', '.join(result['matched'])}")
        st.write(f"Missing Skills: {', '.join(result['missing'])}")
        st.write(f"Suggestions: {result['suggestions']}")
        st.write(f"Evaluation Summary: {result['summary']}")

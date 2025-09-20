import streamlit as st
import os
from src import parsing, scoring, db
import pandas as pd
import altair as alt

st.set_page_config(page_title="Resume Relevance Checker", layout="wide")
st.title("📊 Automated Resume Relevance Check System")

# Upload JD
jd_file = st.file_uploader("Upload Job Description (txt/docx/pdf)", type=["txt","pdf","docx"])
# Upload Resume
resume_file = st.file_uploader("Upload Resume (txt/docx/pdf)", type=["txt","pdf","docx"])

if st.button("Evaluate Resume"):
    if jd_file and resume_file:
        # Extract text
        jd_text = parsing.extract_text(jd_file)
        resume_text = parsing.extract_text(resume_file)

        # Scoring
        score, verdict, matched, missing, suggestions, weights = scoring.evaluate(resume_text, jd_text)

        # Display metrics with rounded score
        st.metric("Relevance Score", f"{score}/100")
        st.subheader(f"Verdict: {verdict}")

        # Graphical visualization of skills
        df_skills = pd.DataFrame({
            "Skill": matched + missing,
            "Status": ["Matched"]*len(matched) + ["Missing"]*len(missing),
            "Weight": weights + [1]*len(missing)  # assign default weight 1 to missing
        })

        st.subheader("Skill Match Overview")
        chart = alt.Chart(df_skills).mark_bar().encode(
            x=alt.X('Skill', sort=None),
            y='Weight',
            color='Status',
            tooltip=['Skill','Status','Weight']
        ).properties(width=700, height=400)
        st.altair_chart(chart, use_container_width=True)

        # Display textual lists
        st.write("✅ Matched Skills:", matched)
        st.write("❌ Missing Skills:", missing)
        st.write("💡 Suggestions:", suggestions)

        # Save results
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

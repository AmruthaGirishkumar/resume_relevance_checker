# app/streamlit_app.py
import streamlit as st
import requests
import json
from pathlib import Path

API_BASE = st.secrets.get("API_BASE", "http://localhost:8000")

st.set_page_config(page_title="Resume Relevance Dashboard", layout="wide")
st.title("Resume Relevance — Evaluator Dashboard")

with st.sidebar:
    st.header("Upload")
    jd_file = st.file_uploader("Job Description (txt/pdf/docx)", type=["txt","pdf","docx"])
    resume_files = st.file_uploader("Resume(s) (multiple)", type=["txt","pdf","docx"], accept_multiple_files=True)
    if st.button("Evaluate & Upload"):
        if jd_file and resume_files:
            # send to backend
            files = [("jd", (jd_file.name, jd_file.getvalue(), jd_file.type))]
            for r in resume_files:
                files.append(("resumes", (r.name, r.getvalue(), r.type)))
            resp = requests.post(f"{API_BASE}/evaluate", files=files, timeout=300)
            st.success("Evaluation completed.")
            st.json(resp.json())

st.header("Recent Evaluations")
resp = requests.get(f"{API_BASE}/evaluations")
if resp.ok:
    rows = resp.json().get("evaluations", [])
    for r in rows:
        st.markdown(f"### {r['resume_name']} — {r['score']:.1f}/100 — {r['verdict']}")
        st.markdown(f"**Matched:** {r['matched'] or 'None'}  •  **Missing:** {r['missing'] or 'None'}")
        st.info(r['feedback'])
        st.divider()
else:
    st.write("No evaluations found or backend not reachable.")

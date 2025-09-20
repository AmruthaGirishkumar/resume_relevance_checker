import streamlit as st
import requests
import subprocess
import time
import atexit
from pathlib import Path

# Start FastAPI backend in background
fastapi_process = subprocess.Popen(
    ["uvicorn", "main:app", "--reload", "--host", "127.0.0.1", "--port", "8000"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

# Ensure FastAPI terminates when Streamlit exits
atexit.register(lambda: fastapi_process.terminate())

# Wait a few seconds to let FastAPI start
time.sleep(3)

# API Base URL
API_BASE = "http://127.0.0.1:8000"

# Streamlit Page Setup
st.set_page_config(page_title="Resume Relevance Dashboard", layout="wide")
st.title("Resume Relevance — Evaluator Dashboard")

# Sidebar: Upload Job Description + Resumes
with st.sidebar:
    st.header("Upload")
    jd_file = st.file_uploader("Job Description (txt/pdf/docx)", type=["txt", "pdf", "docx"])
    resume_files = st.file_uploader("Resume(s) (multiple)", type=["txt", "pdf", "docx"], accept_multiple_files=True)
    
    if st.button("Evaluate & Upload"):
        if jd_file and resume_files:
            try:
                files = [("jd", (jd_file.name, jd_file.getvalue(), jd_file.type))]
                for r in resume_files:
                    files.append(("resumes", (r.name, r.getvalue(), r.type)))
                
                resp = requests.post(f"{API_BASE}/evaluate", files=files, timeout=300)
                resp.raise_for_status()
                st.success("Evaluation completed.")
                st.json(resp.json())
            except requests.exceptions.RequestException as e:
                st.error(f"Error connecting to backend: {e}")

# Display Recent Evaluations
st.header("Recent Evaluations")

try:
    resp = requests.get(f"{API_BASE}/evaluations")
    resp.raise_for_status()
    rows = resp.json().get("evaluations", [])
    
    if not rows:
        st.info("No evaluations found yet.")
    
    for r in rows:
        st.markdown(f"### {r['resume_name']} — {r['score']:.1f}/100 — {r['verdict']}")
        st.markdown(f"**Matched Skills:** {', '.join(r.get('matched', [])) or 'None'}  •  **Missing Skills:** {', '.join(r.get('missing', [])) or 'None'}")
        st.info(r.get("feedback", "No feedback available"))
        st.divider()

except requests.exceptions.RequestException as e:
    st.error(f"Cannot connect to backend: {e}")

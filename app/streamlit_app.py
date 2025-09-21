import streamlit as st
import requests

API_BASE = "http://127.0.0.1:8000"

st.set_page_config(page_title="Resume Relevance Check", layout="wide")

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["📤 Upload & Match", "📊 Results", "🎯 Shortlist"])

# --- Upload Tab ---
with tab1:
    st.header("Upload Job Description & Resumes")
    col1, col2 = st.columns(2)

    with col1:
        jd_file = st.file_uploader("Job Description (PDF/DOCX/TXT)", type=["pdf", "docx", "txt"])

    with col2:
        resumes = st.file_uploader(
            "Resumes (upload multiple)", type=["pdf", "docx", "txt"], accept_multiple_files=True
        )

    if st.button("🚀 Run Evaluation"):
        if jd_file and resumes:
            files = [("jd", (jd_file.name, jd_file.getvalue(), jd_file.type))]
            for r in resumes:
                files.append(("resumes", (r.name, r.getvalue(), r.type)))
            resp = requests.post(f"{API_BASE}/evaluate", files=files)
            if resp.ok:
                st.success("✅ Evaluation Completed!")
            else:
                st.error("⚠️ Error during evaluation.")

# --- Results Tab ---
with tab2:
    st.header("Candidate Results")
    resp = requests.get(f"{API_BASE}/evaluations")

    if resp.ok:
        rows = resp.json().get("evaluations", [])
        if not rows:
            st.info("No evaluations found.")
        else:
            for r in rows:
                color = "green" if r["verdict"]=="High" else "orange" if r["verdict"]=="Medium" else "red"
                with st.container():
                    st.markdown(f"### {r['resume_name']} — :{color}[{r['verdict']}]")
                    st.progress(int(r["score"]))
                    st.write(f"**Matched Skills:** {', '.join(r.get('matched', []))}")
                    st.write(f"**Missing Skills:** {', '.join(r.get('missing', []))}")
                    st.caption(r["feedback"])
                    st.divider()

# --- Shortlist / Filter Tab ---
with tab3:
    st.header("🎯 Resume Shortlisting")
    
    resp = requests.get(f"{API_BASE}/evaluations")
    if resp.ok:
        rows = resp.json().get("evaluations", [])
        
        # Filter controls
        min_score = st.slider("Minimum Score", 0, 100, 60)
        verdict_filter = st.multiselect("Verdict", ["High", "Medium", "Low"], default=["High", "Medium"])
        required_skill = st.text_input("Must-Have Skill (comma separated)")
        export = st.checkbox("Export shortlist as CSV")
        
        # Apply filters
        filtered = [r for r in rows if r["score"] >= min_score]
        if verdict_filter:
            filtered = [r for r in filtered if r["verdict"] in verdict_filter]
        if required_skill:
            skills = [s.strip().lower() for s in required_skill.split(",")]
            filtered = [r for r in filtered if all(s in [m.lower() for m in r.get("matched", [])] for s in skills)]
        
        st.subheader(f"✅ {len(filtered)} candidates shortlisted")
        for r in filtered:
            st.success(f"{r['resume_name']} — {r['score']}% ({r['verdict']})")
        
        # Export option
        if export and filtered:
            import pandas as pd
            df = pd.DataFrame(filtered)
            st.download_button("📥 Download CSV", df.to_csv(index=False), "shortlist.csv", "text/csv")

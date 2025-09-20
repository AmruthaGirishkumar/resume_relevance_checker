from src import parsing, scoring, embeddings, db

def process_resume(jd_file, resume_file, db_path="data/evaluations.db"):
    """
    Full pipeline for a single resume vs job description.
    Returns a dictionary with score, verdict, gaps, and feedback.
    """

    # 1. Extract text from files
    jd_text = parsing.extract_text(jd_file)
    resume_text = parsing.extract_text(resume_file)

    # 2. Evaluate using scoring
    score, verdict, matched, missing, suggestions = scoring.evaluate(resume_text, jd_text)

    # 3. Build summary + likelihood (human-like)
    summary = f"Resume shows strengths in {', '.join([m.title() for m in matched])} " \
              f"but can improve in {', '.join([m.title() for m in missing])}."

    # 4. Store evaluation in DB
    record = {
        "resume_name": resume_file.name,
        "jd_name": jd_file.name,
        "score": round(score, 1),
        "verdict": verdict,
        "matched_skills": [m.title() for m in matched],
        "missing_skills": [m.title() for m in missing],
        "feedback": suggestions,
        "summary": summary
    }
    db.save_evaluation(db_path, record)

    # 5. Return result for frontend
    return record

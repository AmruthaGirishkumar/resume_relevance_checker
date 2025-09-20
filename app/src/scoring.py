from rapidfuzz import fuzz
from src import embeddings
import numpy as np

def hard_match(resume_text, jd_text, skills=["Python","SQL","ML","AI","AWS"]):
    matched, missing = [], []
    resume_lower = resume_text.lower()
    for skill in skills:
        if skill.lower() in resume_lower:
            matched.append(skill)
        else:
            missing.append(skill)
    # Convert to sentence case
    matched = [s.capitalize() for s in matched]
    missing = [s.capitalize() for s in missing]
    return matched, missing

def semantic_score(resume_text, jd_text):
    r_vec = embeddings.get_embedding(resume_text)
    j_vec = embeddings.get_embedding(jd_text)
    sim = np.dot(r_vec, j_vec) / (np.linalg.norm(r_vec) * np.linalg.norm(j_vec))
    return round(sim*100, 2)

def evaluate(resume_text, jd_text):
    matched, missing = hard_match(resume_text, jd_text)
    sem = semantic_score(resume_text, jd_text)
    hard = len(matched) / (len(matched)+len(missing)+1e-6) * 100
    score = round(0.6*sem + 0.4*hard, 1)

    verdict = "High" if score >= 70 else "Medium" if score >= 40 else "Low"

    # Practical human-like suggestions
    suggestions_list = []
    if "Python" in missing:
        suggestions_list.append("Include specific Python projects or libraries you’ve used")
    if "SQL" in missing:
        suggestions_list.append("Highlight database experience with SQL queries or optimizations")
    if "AWS" in missing:
        suggestions_list.append("Showcase cloud deployment or AWS certifications")
    if "ML" in missing:
        suggestions_list.append("Demonstrate machine learning models or AI projects")
    if "AI" in missing:
        suggestions_list.append("Highlight AI-related experience and projects")
    suggestions = " ".join(suggestions_list) if suggestions_list else "Resume is well-aligned with the job description."

    # Combined summary + likelihood in human-like text
    if score >= 70:
        summary = f"Resume is strong and highly aligned with the role. You are likely to be considered for this position."
    elif score >= 40:
        summary = f"Resume shows potential but requires some improvements. Focusing on missing skills can improve chances."
    else:
        summary = f"Resume shows potential but requires significant improvements. Incorporating missing skills can make you a viable candidate."

    return {
        "score": score,
        "verdict": verdict,
        "matched": matched,
        "missing": missing,
        "suggestions": suggestions,
        "summary": summary
    }

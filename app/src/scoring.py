from rapidfuzz import fuzz
from src import embeddings
import numpy as np

def hard_match(resume_text, jd_text, skills=["python","sql","ml","ai","aws"]):
    matched, missing = [], []
    resume_lower = resume_text.lower()
    for skill in skills:
        if skill.lower() in resume_lower:
            matched.append(skill)
        else:
            missing.append(skill)
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
    score = round(0.6*sem + 0.4*hard, 2)
    verdict = "High" if score >= 70 else "Medium" if score >= 40 else "Low"
    suggestions = [f"Add {m}" for m in missing]
    return score, verdict, matched, missing, suggestions

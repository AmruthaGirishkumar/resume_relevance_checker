from rapidfuzz import fuzz
from src import embeddings
import numpy as np

# Assign weights to skills (unique real-time twist)
SKILL_WEIGHTS = {
    "python": 1.5,
    "sql": 1.2,
    "ml": 1.5,
    "ai": 1.5,
    "aws": 1.0
}

def hard_match(resume_text, jd_text, skills=None):
    if skills is None:
        skills = list(SKILL_WEIGHTS.keys())
    matched, missing, weights = [], [], []
    resume_lower = resume_text.lower()
    for skill in skills:
        if skill.lower() in resume_lower:
            matched.append(skill)
            weights.append(SKILL_WEIGHTS[skill])
        else:
            missing.append(skill)
    return matched, missing, weights

def semantic_score(resume_text, jd_text):
    r_vec = embeddings.get_embedding(resume_text)
    j_vec = embeddings.get_embedding(jd_text)
    sim = np.dot(r_vec, j_vec) / (np.linalg.norm(r_vec) * np.linalg.norm(j_vec))
    return round(sim * 100, 1)  # limit to 1 decimal

def evaluate(resume_text, jd_text):
    matched, missing, weights = hard_match(resume_text, jd_text)
    sem = semantic_score(resume_text, jd_text)
    hard = sum(weights) / (sum(weights) + len(missing)) * 100
    score = round(0.6 * sem + 0.4 * hard, 1)
    verdict = "High" if score >= 70 else "Medium" if score >= 40 else "Low"
    suggestions = [f"Add {m}" for m in missing]
    return score, verdict, matched, missing, suggestions, weights

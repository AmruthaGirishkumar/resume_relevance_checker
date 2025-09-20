import numpy as np
from src import embeddings

def hard_match(resume_text, jd_text, skills=["python", "sql", "ml", "ai", "aws"]):
    matched, missing = [], []
    resume_lower = resume_text.lower()
    for skill in skills:
        if skill.lower() in resume_lower:
            matched.append(skill.capitalize())
        else:
            missing.append(skill.capitalize())
    return matched, missing

def semantic_score(resume_text, jd_text):
    r_vec = embeddings.get_embedding(resume_text)
    j_vec = embeddings.get_embedding(jd_text)
    sim = np.dot(r_vec, j_vec) / (np.linalg.norm(r_vec) * np.linalg.norm(j_vec))
    return round(sim * 100, 1)

def generate_suggestions(missing):
    if not missing:
        return "Your resume covers all key skills required for this role."
    suggestions = []
    for skill in missing:
        if skill.lower() == "python":
            suggestions.append("Include specific Python projects or libraries you’ve used.")
        elif skill.lower() == "sql":
            suggestions.append("Highlight database experience with SQL queries or optimizations.")
        elif skill.lower() == "ml":
            suggestions.append("Add any machine learning models or competitions you’ve worked on.")
        elif skill.lower() == "ai":
            suggestions.append("Mention AI-related projects, research, or frameworks (TensorFlow, PyTorch).")
        elif skill.lower() == "aws":
            suggestions.append("Showcase cloud deployment or AWS certifications.")
        else:
            suggestions.append(f"Consider adding experience with {skill}.")
    return " ".join(suggestions)

def generate_summary(score, matched, missing):
    if score >= 80:
        return "Strong alignment with the job requirements, resume looks impressive."
    elif score >= 60:
        return "Decent alignment, but strengthening a few areas could make your profile stronger."
    else:
        return "Resume shows potential but requires significant improvements to match the role."

def calculate_likelihood(score, missing):
    base = score
    penalty = len(missing) * 5
    likelihood = max(0, min(100, base - penalty))
    return round(likelihood, 1)

def evaluate(resume_text, jd_text):
    matched, missing = hard_match(resume_text, jd_text)
    sem = semantic_score(resume_text, jd_text)
    hard = len(matched) / (len(matched) + len(missing) + 1e-6) * 100
    score = round(0.6 * sem + 0.4 * hard, 1)
    verdict = "High" if score >= 70 else "Medium" if score >= 40 else "Low"
    suggestions = generate_suggestions(missing)
    summary = generate_summary(score, matched, missing)
    likelihood = calculate_likelihood(score, missing)
    return {
        "score": score,
        "verdict": verdict,
        "matched": matched,
        "missing": missing,
        "suggestions": suggestions,
        "summary": summary,
        "likelihood": likelihood
    }

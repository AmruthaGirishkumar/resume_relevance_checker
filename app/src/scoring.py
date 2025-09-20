# src/scoring.py
from typing import List, Dict
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from rapidfuzz import fuzz  # pip install rapidfuzz
from . import embeddings, vectorstore
import os

DEFAULT_SKILLS = ["python","sql","machine learning","ai","aws"]

# TF-IDF for document-level similarity (optional)
_tfidf_vectorizer = TfidfVectorizer(stop_words="english")

def hard_skill_match(resume_text: str, jd_text: str, skills=DEFAULT_SKILLS):
    resume_lower = resume_text.lower()
    matched, missing = [], []
    for s in skills:
        if s.lower() in resume_lower:
            matched.append(s.title())
        else:
            missing.append(s.title())
    return matched, missing

def semantic_similarity(resume_text: str, jd_text: str):
    r_vec = embeddings.get_embedding(resume_text)
    j_vec = embeddings.get_embedding(jd_text)
    # cosine similarity:
    num = np.dot(r_vec, j_vec)
    den = np.linalg.norm(r_vec) * np.linalg.norm(j_vec) + 1e-12
    return float(num/den) * 100.0

def weighted_score(resume_text: str, jd_text: str, skills=DEFAULT_SKILLS, weight_sem=0.6, weight_hard=0.4):
    matched, missing = hard_skill_match(resume_text, jd_text, skills)
    sem = semantic_similarity(resume_text, jd_text)
    hard_pct = len(matched) / (len(matched)+len(missing)+1e-12) * 100.0
    score = weight_sem*sem + weight_hard*hard_pct
    return round(score, 1), matched, missing, round(sem,1), round(hard_pct,1)

# Hook to call an LLM (via LangChain/OpenAI) for human-like feedback
def generate_feedback_with_llm(resume_text, jd_text, matched, missing, score):
    # If no OpenAI key, return a deterministic message
    if not os.getenv("OPENAI_API_KEY"):
        if score >= 70:
            return "Resume is strong and well-aligned with the role. Likely to be shortlisted."
        if score >= 40:
            return "Resume is moderately aligned; improving highlighted areas could significantly increase chances."
        return "Resume needs significant improvement; focus on practical projects and key skills."

    # Minimal LangChain/OpenAI usage (showing example, requires openai key)
    from langchain import LLMChain, PromptTemplate
    from langchain.llms import OpenAI
    llm = OpenAI(temperature=0.2)
    template = """
You are an HR reviewer. Given the job description: {jd}
And the candidate's resume extract: {resume}
Matched skills: {matched}
Missing skills: {missing}
Score (0-100): {score}
Write a concise (1-2 sentence) evaluation combining a short summary and a 'what to improve' line.
"""
    prompt = PromptTemplate(input_variables=["jd","resume","matched","missing","score"], template=template)
    chain = LLMChain(llm=llm, prompt=prompt)
    out = chain.run({"jd": jd_text[:1500], "resume": resume_text[:1500], "matched": ", ".join(matched), "missing": ", ".join(missing), "score": score})
    return out.strip()

def evaluate_resume(resume_text: str, jd_text: str, skills=DEFAULT_SKILLS):
    score, matched, missing, sem, hard_pct = weighted_score(resume_text, jd_text, skills)
    feedback = generate_feedback_with_llm(resume_text, jd_text, matched, missing, score)
    return {
        "score": score,
        "matched": matched,
        "missing": missing,
        "semantic": sem,
        "hard_pct": hard_pct,
        "feedback": feedback
    }

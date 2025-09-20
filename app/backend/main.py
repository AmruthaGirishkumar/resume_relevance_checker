# backend/main.py
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import List
from src import parsing, scoring, db
import uvicorn

app = FastAPI(title="Resume Relevance API")
db.init_db()

@app.post("/evaluate")
async def evaluate(jd: UploadFile = File(...), resumes: List[UploadFile] = File(...)):
    jd_bytes = await jd.read()
    # wrap into object-like for parsing (we reuse parsing.extract_text expecting file-like)
    class Uploaded:
        def __init__(self, filename, type, content):
            self.filename = filename
            self.type = type
            self._content = content
        def read(self): return self._content
    jd_obj = Uploaded(jd.filename, jd.content_type, jd_bytes)
    jd_text = parsing.extract_text(jd_obj)

    results = []
    for r in resumes:
        r_bytes = await r.read()
        r_obj = Uploaded(r.filename, r.content_type, r_bytes)
        resume_text = parsing.extract_text(r_obj)
        out = scoring.evaluate_resume(resume_text, jd_text)  # scoring.evaluate_resume calls vector + LLM
        # determine verdict quickly by score
        score = out["score"]
        verdict = "High" if score >= 70 else "Medium" if score >= 40 else "Low"
        rec = {
            "resume_name": r.filename,
            "jd_name": jd.filename,
            "score": score,
            "verdict": verdict,
            "matched": out["matched"],
            "missing": out["missing"],
            "feedback": out["feedback"]
        }
        db.save_evaluation(rec)
        results.append(rec)
    return JSONResponse(content={"results": results})

@app.get("/evaluations")
def get_evals(limit: int = 100):
    rows = db.list_evaluations(limit)
    output = []
    for r in rows:
        output.append({
            "id": r.id,
            "resume_name": r.resume_name,
            "jd_name": r.jd_name,
            "score": r.score,
            "verdict": r.verdict,
            "matched": r.matched,
            "missing": r.missing,
            "feedback": r.feedback
        })
    return {"evaluations": output}

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)

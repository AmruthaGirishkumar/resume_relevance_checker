import sqlite3
import json

def save_evaluation(db_path, record):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resume_name TEXT,
            jd_name TEXT,
            score REAL,
            verdict TEXT,
            matched_skills TEXT,
            missing_skills TEXT,
            suggestions TEXT,
            summary TEXT,
            likelihood REAL
        )
    ''')
    c.execute('''
        INSERT INTO evaluations (resume_name, jd_name, score, verdict, matched_skills, missing_skills, suggestions, summary, likelihood)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        record.get("resume_name", ""),
        record.get("jd_name", ""),
        record["score"],
        record["verdict"],
        json.dumps(record["matched"]),
        json.dumps(record["missing"]),
        record["suggestions"],
        record["summary"],
        record["likelihood"]
    ))
    conn.commit()
    conn.close()

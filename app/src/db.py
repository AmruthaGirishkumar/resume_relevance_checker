import sqlite3

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
        ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    ''')
    c.execute('''
      INSERT INTO evaluations (resume_name, jd_name, score, verdict, matched_skills, missing_skills, suggestions)
      VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        record['resume_name'],
        record['jd_name'],
        record['score'],
        record['verdict'],
        ",".join(record['matched_skills']),
        ",".join(record['missing_skills']),
        "\n".join(record['suggestions'])
    ))
    conn.commit()
    conn.close()
# src/db.py
import os
from sqlalchemy import create_engine, Column, Integer, String, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/evaluations.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Evaluation(Base):
    __tablename__ = "evaluations"
    id = Column(Integer, primary_key=True, index=True)
    resume_name = Column(String, index=True)
    jd_name = Column(String, index=True)
    score = Column(Float)
    verdict = Column(String)
    matched = Column(Text)
    missing = Column(Text)
    feedback = Column(Text)

def init_db():
    os.makedirs("data", exist_ok=True)
    Base.metadata.create_all(bind=engine)

def save_evaluation(record: dict):
    db = SessionLocal()
    ev = Evaluation(
        resume_name = record.get("resume_name"),
        jd_name = record.get("jd_name"),
        score = record.get("score"),
        verdict = record.get("verdict"),
        matched = ", ".join(record.get("matched", [])),
        missing = ", ".join(record.get("missing", [])),
        feedback = record.get("feedback")
    )
    db.add(ev)
    db.commit()
    db.refresh(ev)
    db.close()
    return ev.id

def list_evaluations(limit=100):
    db = SessionLocal()
    rows = db.query(Evaluation).order_by(Evaluation.id.desc()).limit(limit).all()
    db.close()
    return rows

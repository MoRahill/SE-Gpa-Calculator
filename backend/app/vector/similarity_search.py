from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.embedding import StudentEmbedding


def find_similar_students(db: Session, embedding: list[float], exclude_user_id, k: int = 5) -> list[dict]:
    rows = (
        db.execute(
            select(StudentEmbedding)
            .where(StudentEmbedding.user_id != exclude_user_id)
            .where(StudentEmbedding.final_gpa.isnot(None))
            .order_by(StudentEmbedding.embedding.cosine_distance(embedding))
            .limit(k)
        )
        .scalars()
        .all()
    )
    return [{"user_id": str(r.user_id), "final_gpa": float(r.final_gpa)} for r in rows]


def upsert_student_embedding(db: Session, user_id, embedding: list[float], final_gpa: float | None = None):
    existing = db.get(StudentEmbedding, user_id)
    if existing:
        existing.embedding = embedding
        if final_gpa is not None:
            existing.final_gpa = final_gpa
    else:
        db.add(StudentEmbedding(user_id=user_id, embedding=embedding, final_gpa=final_gpa))
    db.commit()

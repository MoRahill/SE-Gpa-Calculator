from sqlalchemy import Column, Numeric, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector

from app.database import Base

EMBEDDING_DIM = 16


class StudentEmbedding(Base):
    __tablename__ = "student_embeddings"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    embedding = Column(Vector(EMBEDDING_DIM), nullable=False)
    final_gpa = Column(Numeric(3, 2), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

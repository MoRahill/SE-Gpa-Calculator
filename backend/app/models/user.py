import uuid

from sqlalchemy import Column, String, Integer, Numeric, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(String, nullable=False, default="student")  # 'student' or 'advisor'
    advisor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    year = Column(Integer, nullable=True)  # class year (1-6), for students
    total_credits_required = Column(Numeric(6, 2), nullable=False, default=120)  # for students
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    courses = relationship("Course", back_populates="user", cascade="all, delete-orphan")

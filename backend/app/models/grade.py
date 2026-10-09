import uuid

from sqlalchemy import Column, String, Numeric, ForeignKey, DateTime, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class GpaSnapshot(Base):
    __tablename__ = "gpa_snapshots"
    __table_args__ = (UniqueConstraint("user_id", "term", name="uq_user_term"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    term = Column(String, nullable=False)
    term_gpa = Column(Numeric(3, 2), nullable=False)
    cumulative_gpa = Column(Numeric(3, 2), nullable=False)
    total_credit_hours = Column(Numeric(6, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

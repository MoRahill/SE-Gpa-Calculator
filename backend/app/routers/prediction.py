from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models.user import User
from app.models.course import Course
from app.auth.dependencies import get_current_user
from app.services.gpa_predictor import predict_next_semester_gpa

router = APIRouter(prefix="/predict", tags=["prediction"])


class PredictionResponse(BaseModel):
    predicted_gpa: float
    method: str
    note: str
    similar_student_count: int


@router.get("/next-semester", response_model=PredictionResponse)
def predict_next_semester(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    courses = db.query(Course).filter(Course.user_id == current_user.id).all()
    course_dicts = [
        {"grade_points": float(c.grade_points), "credit_hours": float(c.credit_hours), "term": c.term}
        for c in courses
    ]
    result = predict_next_semester_gpa(db, current_user.id, course_dicts)
    return PredictionResponse(**result)

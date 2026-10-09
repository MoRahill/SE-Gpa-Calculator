import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, field_validator

from app.database import get_db
from app.models.user import User
from app.models.course import Course
from app.auth.dependencies import get_current_user
from app.services.gpa_calculator import grade_to_points, calculate_term_and_cumulative_gpa
from app.vector.embeddings import generate_embedding
from app.vector.similarity_search import upsert_student_embedding

router = APIRouter(prefix="/gpa", tags=["gpa"])


class AddCourseRequest(BaseModel):
    course_name: str
    credit_hours: float
    grade: str
    term: str


class CourseOut(BaseModel):
    id: str
    course_name: str
    credit_hours: float
    grade: str
    grade_points: float
    term: str

    class Config:
        from_attributes = True

    @field_validator("id", mode="before")
    @classmethod
    def coerce_id_to_str(cls, value):
        return str(value)


class GpaSummary(BaseModel):
    courses: list[CourseOut]
    term_gpa: float
    cumulative_gpa: float
    total_credit_hours: float


def _get_courses_as_dicts(db: Session, user_id) -> list[dict]:
    courses = db.query(Course).filter(Course.user_id == user_id).order_by(Course.created_at).all()
    return [
        {"grade_points": float(c.grade_points), "credit_hours": float(c.credit_hours), "term": c.term}
        for c in courses
    ]


@router.post("/courses", response_model=CourseOut, status_code=201)
def add_course(payload: AddCourseRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        points = grade_to_points(payload.grade)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    course = Course(
        id=uuid.uuid4(),
        user_id=current_user.id,
        course_name=payload.course_name,
        credit_hours=payload.credit_hours,
        grade=payload.grade.upper(),
        grade_points=points,
        term=payload.term,
    )
    db.add(course)
    db.commit()
    db.refresh(course)

    embedding = generate_embedding(_get_courses_as_dicts(db, current_user.id))
    upsert_student_embedding(db, current_user.id, embedding)

    return CourseOut.model_validate(course)


@router.get("/summary", response_model=GpaSummary)
def get_summary(term: str | None = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    courses = db.query(Course).filter(Course.user_id == current_user.id).order_by(Course.created_at).all()
    course_dicts = [
        {"grade_points": float(c.grade_points), "credit_hours": float(c.credit_hours), "term": c.term}
        for c in courses
    ]

    if not course_dicts:
        return GpaSummary(courses=[], term_gpa=0.0, cumulative_gpa=0.0, total_credit_hours=0.0)

    target_term = term or courses[-1].term
    result = calculate_term_and_cumulative_gpa(course_dicts, target_term)

    return GpaSummary(
        courses=[CourseOut.model_validate(c) for c in courses],
        term_gpa=result["term_gpa"],
        cumulative_gpa=result["cumulative_gpa"],
        total_credit_hours=result["total_credit_hours"],
    )


@router.delete("/courses/{course_id}", status_code=204)
def delete_course(course_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    course = db.get(Course, course_id)
    if not course or course.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Course not found")
    db.delete(course)
    db.commit()

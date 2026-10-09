import re

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models.user import User
from app.models.course import Course
from app.auth.dependencies import require_advisor
from app.services.gpa_calculator import calculate_gpa
from app.services.degree_progress import calculate_degree_progress
from app.services.chart_generator import generate_gpa_trend_chart
from app.services.pdf_report import generate_student_report_pdf

router = APIRouter(prefix="/advisor", tags=["advisor"])


class AdviseeSummary(BaseModel):
    id: str
    full_name: str
    email: str
    year: int | None = None
    cumulative_gpa: float


class SemesterBreakdown(BaseModel):
    term: str
    gpa: float
    courses: list[dict]


class DegreeProgress(BaseModel):
    credits_completed: float
    credits_required: float
    credits_remaining: float
    courses_remaining_estimate: int | None
    semesters_remaining_estimate: int | None


class AdviseeDetail(BaseModel):
    id: str
    full_name: str
    email: str
    year: int | None = None
    cumulative_gpa: float
    degree_progress: DegreeProgress
    semesters: list[SemesterBreakdown]


def _semester_sort_key(term: str) -> int:
    match = re.search(r"\d+", term)
    return int(match.group()) if match else 0


def _get_student_courses(db: Session, student_id) -> list[Course]:
    return db.query(Course).filter(Course.user_id == student_id).order_by(Course.created_at).all()


def _course_dicts(courses: list[Course]) -> list[dict]:
    return [
        {
            "course_name": c.course_name,
            "grade": c.grade,
            "grade_points": float(c.grade_points),
            "credit_hours": float(c.credit_hours),
            "term": c.term,
        }
        for c in courses
    ]


def _build_semester_breakdown(course_dicts: list[dict]) -> list[dict]:
    groups: dict[str, list[dict]] = {}
    for c in course_dicts:
        groups.setdefault(c["term"], []).append(c)

    semesters = []
    for term, courses in groups.items():
        gpa = calculate_gpa(courses)
        semesters.append({"term": term, "gpa": gpa, "courses": courses})

    semesters.sort(key=lambda s: _semester_sort_key(s["term"]))
    return semesters


def _require_own_advisee(db: Session, advisor: User, student_id: str) -> User:
    student = db.get(User, student_id)
    if not student or student.advisor_id != advisor.id:
        raise HTTPException(status_code=404, detail="Advisee not found")
    return student


@router.get("/advisees", response_model=list[AdviseeSummary])
def list_advisees(db: Session = Depends(get_db), advisor: User = Depends(require_advisor)):
    students = db.query(User).filter(User.advisor_id == advisor.id, User.role == "student").all()

    results = []
    for student in students:
        course_dicts = _course_dicts(_get_student_courses(db, student.id))
        cumulative_gpa = calculate_gpa(course_dicts) if course_dicts else 0.0
        results.append(AdviseeSummary(
            id=str(student.id), full_name=student.full_name, email=student.email,
            year=student.year, cumulative_gpa=cumulative_gpa,
        ))

    return results


@router.get("/advisees/{student_id}", response_model=AdviseeDetail)
def get_advisee_detail(student_id: str, db: Session = Depends(get_db), advisor: User = Depends(require_advisor)):
    student = _require_own_advisee(db, advisor, student_id)
    course_dicts = _course_dicts(_get_student_courses(db, student.id))

    cumulative_gpa = calculate_gpa(course_dicts) if course_dicts else 0.0
    degree_progress = calculate_degree_progress(course_dicts, float(student.total_credits_required))
    semesters = _build_semester_breakdown(course_dicts)

    return AdviseeDetail(
        id=str(student.id), full_name=student.full_name, email=student.email, year=student.year,
        cumulative_gpa=cumulative_gpa,
        degree_progress=DegreeProgress(**degree_progress),
        semesters=[SemesterBreakdown(**s) for s in semesters],
    )


@router.get("/advisees/{student_id}/chart.png")
def get_advisee_chart(student_id: str, db: Session = Depends(get_db), advisor: User = Depends(require_advisor)):
    student = _require_own_advisee(db, advisor, student_id)
    course_dicts = _course_dicts(_get_student_courses(db, student.id))
    semesters = _build_semester_breakdown(course_dicts)

    png_bytes = generate_gpa_trend_chart([{"term": s["term"], "gpa": s["gpa"]} for s in semesters])
    return Response(content=png_bytes, media_type="image/png")


@router.get("/advisees/{student_id}/export.pdf")
def export_advisee_report(student_id: str, db: Session = Depends(get_db), advisor: User = Depends(require_advisor)):
    student = _require_own_advisee(db, advisor, student_id)
    course_dicts = _course_dicts(_get_student_courses(db, student.id))

    cumulative_gpa = calculate_gpa(course_dicts) if course_dicts else 0.0
    degree_progress = calculate_degree_progress(course_dicts, float(student.total_credits_required))
    semesters = _build_semester_breakdown(course_dicts)
    chart_png = generate_gpa_trend_chart([{"term": s["term"], "gpa": s["gpa"]} for s in semesters])

    pdf_bytes = generate_student_report_pdf(
        student_name=student.full_name,
        student_email=student.email,
        advisor_name=advisor.full_name,
        cumulative_gpa=cumulative_gpa,
        degree_progress=degree_progress,
        semesters=semesters,
        chart_png_bytes=chart_png,
    )

    filename = f"{student.full_name.replace(' ', '_')}_report.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

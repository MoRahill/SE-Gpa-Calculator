import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.gpa_calculator import grade_to_points, calculate_gpa, calculate_term_and_cumulative_gpa
from app.services.degree_progress import calculate_degree_progress


def test_grade_to_points():
    assert grade_to_points("A+") == 4.00
    assert grade_to_points("A") == 3.75
    assert grade_to_points("b+") == 3.50
    assert grade_to_points("F") == 0.00


def test_calculate_gpa_single_course():
    courses = [{"grade_points": 4.0, "credit_hours": 3}]
    assert calculate_gpa(courses) == 4.0


def test_calculate_gpa_weighted_average():
    courses = [
        {"grade_points": 4.00, "credit_hours": 3},
        {"grade_points": 2.75, "credit_hours": 1},
    ]
    assert calculate_gpa(courses) == 3.69


def test_calculate_gpa_empty():
    assert calculate_gpa([]) == 0.0


def test_term_and_cumulative_gpa():
    courses = [
        {"grade_points": 4.00, "credit_hours": 3, "term": "Semester 1"},
        {"grade_points": 3.25, "credit_hours": 3, "term": "Semester 2"},
    ]
    result = calculate_term_and_cumulative_gpa(courses, "Semester 2")
    assert result["term_gpa"] == 3.25
    assert result["cumulative_gpa"] == 3.63
    assert result["total_credit_hours"] == 6.0


def test_degree_progress_basic():
    courses = [
        {"credit_hours": 15, "term": "Semester 1"},
        {"credit_hours": 15, "term": "Semester 2"},
    ]
    result = calculate_degree_progress(courses, total_credits_required=120)
    assert result["credits_completed"] == 30
    assert result["credits_remaining"] == 90
    # avg 15 credits/semester -> 6 semesters remaining
    assert result["semesters_remaining_estimate"] == 6


def test_degree_progress_no_courses_yet():
    result = calculate_degree_progress([], total_credits_required=120)
    assert result["credits_completed"] == 0
    assert result["credits_remaining"] == 120
    assert result["semesters_remaining_estimate"] == 8  # falls back to 15/semester default

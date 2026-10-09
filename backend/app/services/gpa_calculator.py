"""Core GPA math, isolated from the HTTP layer so it's easy to unit test."""

from decimal import Decimal, ROUND_HALF_UP
from typing import Iterable

# Custom 4.0 scale (0.25 steps, no minus grades): A+ is 4.0, A is 3.75, B+ is 3.5, etc.
GRADE_POINTS = {
    "A+": 4.00,
    "A": 3.75,
    "B+": 3.50,
    "B": 3.25,
    "C+": 3.00,
    "C": 2.75,
    "D+": 2.50,
    "D": 2.25,
    "F": 0.00,
}


def grade_to_points(letter_grade: str) -> float:
    letter_grade = letter_grade.strip().upper()
    if letter_grade not in GRADE_POINTS:
        raise ValueError(f"Unknown letter grade: {letter_grade!r}")
    return GRADE_POINTS[letter_grade]


def calculate_gpa(courses: Iterable[dict]) -> float:
    """courses: iterable of {'grade_points': float, 'credit_hours': float}"""
    total_points = Decimal("0")
    total_credits = Decimal("0")

    for course in courses:
        credits = Decimal(str(course["credit_hours"]))
        points = Decimal(str(course["grade_points"]))
        total_points += points * credits
        total_credits += credits

    if total_credits == 0:
        return 0.0

    gpa = (total_points / total_credits).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return float(gpa)


def calculate_term_and_cumulative_gpa(all_courses: list[dict], term: str) -> dict:
    term_courses = [c for c in all_courses if c["term"] == term]

    return {
        "term_gpa": calculate_gpa(term_courses),
        "cumulative_gpa": calculate_gpa(all_courses),
        "total_credit_hours": float(sum(Decimal(str(c["credit_hours"])) for c in all_courses)),
    }

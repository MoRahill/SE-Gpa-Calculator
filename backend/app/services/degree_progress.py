"""Estimates how much is left before a student graduates, based on their
course history so far and how many credits their program requires.

These are estimates, not official degree-audit numbers (a real registrar
system would check specific requirement categories, prerequisites, etc.) -
this gives an advisor a quick, honest approximation to talk through with
the student, clearly labeled as such on the frontend.
"""

import math


def calculate_degree_progress(courses: list[dict], total_credits_required: float) -> dict:
    """courses: list of {'credit_hours': float, 'term': str}"""
    credits_completed = sum(c["credit_hours"] for c in courses)
    credits_remaining = max(total_credits_required - credits_completed, 0.0)

    num_courses_taken = len(courses)
    num_semesters_taken = len(set(c["term"] for c in courses))

    # Fall back to reasonable defaults when there's no history yet to estimate from.
    avg_credits_per_semester = (credits_completed / num_semesters_taken) if num_semesters_taken > 0 else 15.0
    avg_credits_per_course = (credits_completed / num_courses_taken) if num_courses_taken > 0 else 3.0

    semesters_remaining = math.ceil(credits_remaining / avg_credits_per_semester) if avg_credits_per_semester > 0 else None
    courses_remaining = math.ceil(credits_remaining / avg_credits_per_course) if avg_credits_per_course > 0 else None

    return {
        "credits_completed": round(credits_completed, 2),
        "credits_required": round(total_credits_required, 2),
        "credits_remaining": round(credits_remaining, 2),
        "courses_remaining_estimate": courses_remaining,
        "semesters_remaining_estimate": semesters_remaining,
    }

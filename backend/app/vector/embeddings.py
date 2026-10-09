"""Builds a numeric 'fingerprint' vector for a student's academic profile
using hand-crafted statistical features (no external embedding API key
required)."""

from app.models.embedding import EMBEDDING_DIM


def generate_embedding(courses: list[dict]) -> list[float]:
    if not courses:
        return [0.0] * EMBEDDING_DIM

    grade_points = [c["grade_points"] for c in courses]
    credit_hours = [c["credit_hours"] for c in courses]
    terms = sorted(set(c["term"] for c in courses))

    avg_gp = sum(grade_points) / len(grade_points)
    variance = sum((g - avg_gp) ** 2 for g in grade_points) / len(grade_points)
    avg_credits = sum(credit_hours) / len(credit_hours)
    num_terms = len(terms)
    num_courses = len(courses)

    midpoint = len(grade_points) // 2 or 1
    first_half_avg = sum(grade_points[:midpoint]) / midpoint
    second_half_avg = sum(grade_points[midpoint:]) / max(len(grade_points[midpoint:]), 1)
    trend = second_half_avg - first_half_avg

    buckets = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
    for gp in grade_points:
        if gp >= 3.5:
            buckets["A"] += 1
        elif gp >= 3.0:
            buckets["B"] += 1
        elif gp >= 2.5:
            buckets["C"] += 1
        elif gp >= 2.0:
            buckets["D"] += 1
        else:
            buckets["F"] += 1
    bucket_props = [v / num_courses for v in buckets.values()]

    features = [avg_gp, variance, avg_credits, float(num_terms), float(num_courses), trend] + bucket_props

    if len(features) < EMBEDDING_DIM:
        features += [0.0] * (EMBEDDING_DIM - len(features))
    return features[:EMBEDDING_DIM]

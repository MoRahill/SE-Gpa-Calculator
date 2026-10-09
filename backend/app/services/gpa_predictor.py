from sqlalchemy.orm import Session

from app.vector.embeddings import generate_embedding
from app.vector.similarity_search import find_similar_students


def _trend_based_prediction(courses: list[dict]) -> float:
    if not courses:
        return 0.0
    terms = sorted(set(c["term"] for c in courses))
    term_gpas = []
    for term in terms:
        term_courses = [c for c in courses if c["term"] == term]
        total_credits = sum(c["credit_hours"] for c in term_courses)
        if total_credits == 0:
            continue
        weighted = sum(c["grade_points"] * c["credit_hours"] for c in term_courses) / total_credits
        term_gpas.append(weighted)

    if not term_gpas:
        return 0.0
    weights = list(range(1, len(term_gpas) + 1))
    weighted_sum = sum(g * w for g, w in zip(term_gpas, weights))
    return round(weighted_sum / sum(weights), 2)


def predict_next_semester_gpa(db: Session, user_id, courses: list[dict]) -> dict:
    trend_prediction = _trend_based_prediction(courses)
    embedding = generate_embedding(courses)
    similar_students = find_similar_students(db, embedding, exclude_user_id=user_id, k=5)

    if not similar_students:
        return {
            "predicted_gpa": trend_prediction,
            "method": "trend_only",
            "note": "Not enough historical student data yet for similarity-based prediction. "
                    "Using your own grade trend instead.",
            "similar_student_count": 0,
        }

    similarity_avg = sum(s["final_gpa"] for s in similar_students) / len(similar_students)
    blended = round(0.6 * trend_prediction + 0.4 * similarity_avg, 2)

    return {
        "predicted_gpa": blended,
        "method": "trend_plus_similarity",
        "note": f"Based on your grade trend and {len(similar_students)} similar student profiles.",
        "similar_student_count": len(similar_students),
    }

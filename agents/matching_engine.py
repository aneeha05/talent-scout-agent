from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def compute_skill_overlap(required_skills: list, candidate_skills: list) -> float:
    if not required_skills:
        return 0.5
    required_lower = {s.lower() for s in required_skills}
    candidate_lower = {s.lower() for s in candidate_skills}
    matched = required_lower.intersection(candidate_lower)
    return len(matched) / len(required_lower)

def compute_semantic_similarity(jd_summary: str, candidate_bio: str) -> float:
    if not jd_summary or not candidate_bio:
        return 0.3
    try:
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform([jd_summary, candidate_bio])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return float(similarity)
    except Exception:
        return 0.3

def compute_experience_score(min_years: int, candidate_years: int) -> float:
    if candidate_years < min_years:
        return max(0.0, candidate_years / max(min_years, 1))
    elif candidate_years <= min_years + 4:
        return 1.0
    else:
        return max(0.5, 1.0 - (candidate_years - min_years - 4) * 0.05)

def compute_match_score(parsed_jd: dict, candidate: dict) -> dict:
    skill_score = compute_skill_overlap(
        parsed_jd.get("required_skills", []),
        candidate.get("skills", [])
    )
    semantic_score = compute_semantic_similarity(
        parsed_jd.get("role_summary", ""),
        candidate.get("bio", "")
    )
    exp_score = compute_experience_score(
        parsed_jd.get("min_years_experience", 0),
        candidate.get("years_experience", 0)
    )

    raw_score = (skill_score * 0.50) + (semantic_score * 0.30) + (exp_score * 0.20)
    match_score = round(raw_score * 100, 1)

    matched_skills = list(
        {s.lower() for s in parsed_jd.get("required_skills", [])}
        .intersection({s.lower() for s in candidate.get("skills", [])})
    )

    return {
        "match_score": match_score,
        "breakdown": {
            "skill_overlap_pct": round(skill_score * 100, 1),
            "semantic_similarity_pct": round(semantic_score * 100, 1),
            "experience_fit_pct": round(exp_score * 100, 1),
            "matched_skills": matched_skills
        }
    }
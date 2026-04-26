from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Load once — this model is free and runs locally (downloads ~90MB first run)
model = SentenceTransformer('all-MiniLM-L6-v2')

def compute_skill_overlap(required_skills: list, candidate_skills: list) -> float:
    """Hard skill match: what % of required skills does the candidate have?"""
    if not required_skills:
        return 0.5
    required_lower = {s.lower() for s in required_skills}
    candidate_lower = {s.lower() for s in candidate_skills}
    matched = required_lower.intersection(candidate_lower)
    return len(matched) / len(required_lower)

def compute_semantic_similarity(jd_summary: str, candidate_bio: str) -> float:
    """Semantic similarity between JD context and candidate bio using embeddings."""
    if not jd_summary or not candidate_bio:
        return 0.3
    embeddings = model.encode([jd_summary, candidate_bio])
    similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
    return float(similarity)

def compute_experience_score(min_years: int, candidate_years: int) -> float:
    """Score based on experience. Penalise too little, slightly penalise too much."""
    if candidate_years < min_years:
        return max(0.0, candidate_years / min_years)
    elif candidate_years <= min_years + 4:
        return 1.0
    else:
        # Very over-qualified — might not be interested
        return max(0.5, 1.0 - (candidate_years - min_years - 4) * 0.05)

def compute_match_score(parsed_jd: dict, candidate: dict) -> dict:
    """
    Computes the Match Score (0–100) with full explainability.
    Returns score and breakdown dict.
    """
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
    
    # Weighted combination
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
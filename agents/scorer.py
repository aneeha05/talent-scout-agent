import pandas as pd

def build_ranked_shortlist(candidates_with_scores: list) -> pd.DataFrame:
    """
    Takes a list of candidates each with match_score and interest_score.
    Computes a combined rank score and returns a sorted DataFrame.
    """
    rows = []
    for c in candidates_with_scores:
        combined = round((c["match_score"] * 0.6) + (c["interest_score"] * 0.4), 1)
        rows.append({
            "Name": c["name"],
            "Title": c["title"],
            "Match Score": c["match_score"],
            "Interest Score": c["interest_score"],
            "Combined Score": combined,
            "Matched Skills": ", ".join(c.get("matched_skills", [])),
            "Interest Level": c["interest_level"],
            "Location": c["location"],
            "Years Exp": c["years_experience"]
        })
    
    df = pd.DataFrame(rows)
    df = df.sort_values("Combined Score", ascending=False).reset_index(drop=True)
    df.index = df.index + 1  # 1-based rank
    df.index.name = "Rank"
    return df
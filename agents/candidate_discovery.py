import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

def load_mock_candidates() -> list:
    """Load the local mock candidate database."""
    path = os.path.join(os.path.dirname(__file__), '..', 'data', 'mock_candidates.json')
    with open(path, 'r') as f:
        return json.load(f)

def enrich_with_github(candidate: dict) -> dict:
    """
    Optionally fetch real GitHub data to enrich a candidate profile.
    Uses free GitHub API (60 req/hr unauthenticated, 5000/hr with token).
    """
    if not candidate.get("github"):
        return candidate
    
    headers = {}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    
    try:
        url = f"https://api.github.com/users/{candidate['github']}"
        resp = requests.get(url, headers=headers, timeout=5)
        if resp.status_code == 200:
            gh_data = resp.json()
            candidate["github_public_repos"] = gh_data.get("public_repos", 0)
            candidate["github_followers"] = gh_data.get("followers", 0)
            candidate["github_bio"] = gh_data.get("bio", "")
    except Exception:
        pass  # GitHub enrichment is optional — don't crash if it fails
    
    return candidate

def discover_candidates(parsed_jd: dict) -> list:
    """
    Main discovery function. Loads mock candidates and optionally enriches
    with real GitHub data. Returns list of candidate dicts.
    """
    candidates = load_mock_candidates()
    
    # Filter by minimum experience
    min_exp = parsed_jd.get("min_years_experience", 0)
    candidates = [c for c in candidates if c.get("years_experience", 0) >= max(0, min_exp - 2)]
    
    # Enrich top candidates with GitHub data
    enriched = []
    for candidate in candidates:
        enriched.append(enrich_with_github(candidate))
    
    return enriched
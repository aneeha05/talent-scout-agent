# Sample Output — Senior Backend Engineer JD

## Parsed JD Structure
- Title: Senior Backend Engineer
- Required Skills: Python, FastAPI, PostgreSQL, AWS, Docker
- Min Experience: 4 years
- Seniority: Senior
- Industry: Fintech

## Ranked Shortlist

| Rank | Name | Match Score | Interest Score | Combined Score |
|------|------|-------------|----------------|----------------|
| 1 | Priya Sharma | 82.1 | 76.0 | 79.9 |
| 2 | Vikram Nair | 74.3 | 81.0 | 77.0 |
| 3 | Sneha Kulkarni | 71.2 | 89.0 | 78.5 |

## Scoring Explanation

### Match Score (0–100)
| Component | Weight | Method |
|-----------|--------|--------|
| Skill overlap | 50% | Exact keyword match of required vs candidate skills |
| Semantic similarity | 30% | Sentence-BERT cosine similarity (JD summary vs bio) |
| Experience fit | 20% | Smooth penalty for under/over qualification |

### Interest Score (0–100)
| Signal | Impact |
|--------|--------|
| Availability: actively_looking | Base: 65 |
| Availability: open_to_opportunities | Base: 50 |
| Availability: not_looking | Base: 25 |
| Positive keywords in conversation | +8 each |
| Negative keywords in conversation | -10 each |

### Final Rank Formula
Combined Score = (Match Score × 0.6) + (Interest Score × 0.4)
import anthropic
import os
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

INTEREST_SIGNALS = {
    "high": ["excited", "definitely", "love to", "great opportunity", "sounds perfect",
             "when can we", "very interested", "yes absolutely", "looking forward"],
    "medium": ["could be interesting", "tell me more", "open to", "depends", "maybe",
               "would consider", "curious"],
    "low": ["not really", "happy where I am", "not looking", "too busy",
            "not interested", "pass", "not the right fit"]
}

def simulate_outreach_conversation(candidate: dict, parsed_jd: dict) -> dict:
    availability = candidate.get("availability", "unknown")

    system_prompt = f"""You are {candidate['name']}, a {candidate['title']} with {candidate['years_experience']} 
years of experience. Your skills include: {', '.join(candidate['skills'])}.
Your current availability status is: {availability}.
Bio: {candidate['bio']}

You are responding to a recruiter reaching out about a job opportunity. 
Respond authentically based on your availability status:
- If 'actively_looking': show genuine interest, ask questions
- If 'open_to_opportunities': show moderate interest, want more details
- If 'not_looking': be polite but explain you are currently happy

Keep responses conversational, 2-4 sentences. Sound like a real professional on LinkedIn."""

    recruiter_message = f"""Hi {candidate['name'].split()[0]}! I came across your profile and was 
really impressed by your background in {', '.join(candidate['skills'][:3])}.

We are hiring a {parsed_jd['title']}. The role involves {parsed_jd['role_summary']}. 
With your {candidate['years_experience']} years of experience, you seem like a great fit. 
Would you be open to a quick 15-minute chat this week?"""

    follow_up = "Great to hear from you! Could you share what kind of role would excite you most right now, and what matters most to you in your next move?"

    # Turn 1
    messages = [{"role": "user", "content": recruiter_message}]
    resp1 = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        system=system_prompt,
        messages=messages
    )
    candidate_reply_1 = resp1.content[0].text.strip()

    # Turn 2
    messages.append({"role": "assistant", "content": candidate_reply_1})
    messages.append({"role": "user", "content": follow_up})
    resp2 = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        system=system_prompt,
        messages=messages
    )
    candidate_reply_2 = resp2.content[0].text.strip()

    conversation = [
        {"role": "Recruiter", "message": recruiter_message},
        {"role": candidate['name'], "message": candidate_reply_1},
        {"role": "Recruiter", "message": follow_up},
        {"role": candidate['name'], "message": candidate_reply_2}
    ]

    interest_score = _score_interest(candidate_reply_1 + " " + candidate_reply_2, availability)

    return {
        "conversation": conversation,
        "interest_score": interest_score,
        "interest_level": "high" if interest_score >= 70 else "medium" if interest_score >= 40 else "low"
    }


def _score_interest(combined_text: str, availability: str) -> int:
    text_lower = combined_text.lower()

    if availability == "actively_looking":
        score = 65
    elif availability == "open_to_opportunities":
        score = 50
    elif availability == "not_looking":
        score = 25
    else:
        score = 40

    for word in INTEREST_SIGNALS["high"]:
        if word in text_lower:
            score += 8
    for word in INTEREST_SIGNALS["medium"]:
        if word in text_lower:
            score += 3
    for word in INTEREST_SIGNALS["low"]:
        if word in text_lower:
            score -= 10

    return max(0, min(100, score))
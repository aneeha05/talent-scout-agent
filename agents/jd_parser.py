import json
import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def parse_job_description(jd_text: str) -> dict:
    prompt = f"""You are an expert technical recruiter. Parse the following job description 
and extract structured information. Return ONLY a valid JSON object with NO extra text.

Job Description:
{jd_text}

Return this exact JSON structure:
{{
  "title": "exact job title",
  "required_skills": ["skill1", "skill2"],
  "nice_to_have_skills": ["skill1", "skill2"],
  "min_years_experience": 3,
  "seniority": "junior|mid|senior|lead|principal",
  "industry": "fintech|edtech|healthtech|ecommerce|saas|other",
  "role_summary": "2-sentence summary of the core role"
}}"""

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = message.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    return json.loads(raw.strip())
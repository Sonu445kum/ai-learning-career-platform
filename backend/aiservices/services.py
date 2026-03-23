import json
import PyPDF2
from io import BytesIO
from openai import OpenAI
from django.conf import settings


client = OpenAI(api_key=settings.OPENAI_API_KEY)

CAREER_SYSTEM_PROMPT = """You are an expert AI career counselor and learning advisor.
You help users with:
- Career guidance and roadmaps
- Skill gap analysis
- Job search strategies
- Interview preparation
- Course recommendations
- Resume improvement tips

Respond in a clear, structured, friendly and professional manner.
Always provide actionable advice. Use bullet points and headers where appropriate.
"""

RESUME_ANALYSIS_PROMPT = """You are a professional resume reviewer and ATS expert.
Analyze the provided resume and return a JSON response with the following structure:
{
  "overall_score": <float 0-100>,
  "ats_score": <float 0-100>,
  "summary": "<brief overall assessment>",
  "strengths": ["<strength1>", "<strength2>", ...],
  "weaknesses": ["<weakness1>", "<weakness2>", ...],
  "suggestions": ["<actionable suggestion1>", "<suggestion2>", ...],
  "keywords_found": ["<keyword1>", ...],
  "keywords_missing": ["<important missing keyword1>", ...]
}
Return ONLY the JSON object. Be specific and detailed.
"""


def extract_text_from_pdf(file_obj):
    """Extract text from a PDF file object."""
    try:
        reader = PyPDF2.PdfReader(BytesIO(file_obj.read()))
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        raise ValueError(f"Failed to extract PDF text: {str(e)}")


def chat_with_ai(messages: list, session_context: str = "") -> dict:
    """
    Send messages to OpenAI and return response with token usage.
    messages = [{"role": "user"/"assistant", "content": "..."}]
    """
    system_messages = [{"role": "system", "content": CAREER_SYSTEM_PROMPT}]
    if session_context:
        system_messages.append(
            {"role": "system", "content": f"User context: {session_context}"})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=system_messages + messages,
        max_tokens=1024,
        temperature=0.7,
    )
    return {
        "content": response.choices[0].message.content,
        "tokens_used": response.usage.total_tokens,
        "finish_reason": response.choices[0].finish_reason,
    }


def analyze_resume(resume_text: str, job_description: str = "") -> dict:
    """Analyze resume using AI and return structured feedback."""
    user_prompt = f"Resume:\n{resume_text}"
    if job_description:
        user_prompt += f"\n\nTarget Job Description:\n{job_description}"

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": RESUME_ANALYSIS_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=2000,
        temperature=0.3,
        response_format={"type": "json_object"},
    )
    raw = response.choices[0].message.content
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {
            "overall_score": 50.0,
            "ats_score": 50.0,
            "summary": "Analysis completed.",
            "strengths": [],
            "weaknesses": [],
            "suggestions": ["Please try uploading a clearer resume."],
            "keywords_found": [],
            "keywords_missing": [],
        }


def generate_career_roadmap(target_role: str, current_skills: list, experience_years: int) -> dict:
    """Generate a step-by-step career roadmap."""
    prompt = f"""Create a detailed career roadmap for someone wanting to become a {target_role}.
Current skills: {', '.join(current_skills) or 'None listed'}
Years of experience: {experience_years}

Return a JSON with this structure:
{{
  "title": "<roadmap title>",
  "estimated_timeline": "<e.g. 6-12 months>",
  "phases": [
    {{
      "phase": 1,
      "name": "<phase name>",
      "duration": "<e.g. 1-2 months>",
      "goals": ["<goal1>", "<goal2>"],
      "skills_to_learn": ["<skill1>", "<skill2>"],
      "resources": ["<resource1>", "<resource2>"],
      "milestones": ["<milestone1>"]
    }}
  ],
  "final_skills": ["<skill1>", "<skill2>"],
  "job_titles": ["<related job title1>", "<title2>"],
  "avg_salary_range": "<e.g. ₹8-15 LPA>"
}}
Return ONLY valid JSON."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000,
        temperature=0.5,
        response_format={"type": "json_object"},
    )
    try:
        return json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        return {"error": "Failed to generate roadmap. Please try again."}


def generate_quiz_questions(topic: str, difficulty: str = "medium", count: int = 5) -> list:
    """Generate quiz questions for a given topic."""
    prompt = f"""Generate {count} multiple choice quiz questions about "{topic}" at {difficulty} difficulty.
Return JSON array:
[
  {{
    "question": "<question text>",
    "options": ["A) <opt>", "B) <opt>", "C) <opt>", "D) <opt>"],
    "correct_answer": "A",
    "explanation": "<why this is correct>"
  }}
]
Return ONLY the JSON array."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000,
        temperature=0.6,
        response_format={"type": "json_object"},
    )
    try:
        data = json.loads(response.choices[0].message.content)
        return data if isinstance(data, list) else data.get('questions', [])
    except Exception:
        return []

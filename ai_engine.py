import os
from openai import OpenAI

MODEL = "llama-3.3-70b-versatile"


def _get_client() -> OpenAI:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is not set. Add it to your .env file: GROQ_API_KEY=your_key_here"
        )
    return OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=api_key,
    )


def _stream(messages: list):
    client = _get_client()
    stream = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        stream=True,
        max_tokens=2048,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta


def generate_cover_letter(cv_text: str, job_description: str):
    return _stream([
        {
            "role": "system",
            "content": "You are an expert career consultant who writes compelling, personalized cover letters.",
        },
        {
            "role": "user",
            "content": f"""Write a tailored, professional cover letter based on the CV and job description below.

CV:
{cv_text}

Job Description:
{job_description}

Requirements:
- Open with a strong specific hook (not "I am writing to apply for...")
- Highlight 2-3 experiences from the CV that directly match the job
- Show genuine enthusiasm for the role
- End with a confident call to action
- Keep it to 3-4 paragraphs, professional but warm tone""",
        },
    ])


def generate_cv_suggestions(cv_text: str, job_description: str):
    return _stream([
        {
            "role": "system",
            "content": "You are an expert resume writer and career coach who gives specific, actionable advice.",
        },
        {
            "role": "user",
            "content": f"""Analyze this CV against the job description and give specific improvement suggestions.

CV:
{cv_text}

Job Description:
{job_description}

Provide specific suggestions for:
1. Missing keywords or skills from the job description to add
2. Sections to add or expand
3. Achievements to quantify with numbers and metrics
4. Formatting or structure improvements
5. Experience gaps to address

Reference actual content from both the CV and job description — be specific, not generic.""",
        },
    ])


def generate_skills_highlight(cv_text: str, job_description: str):
    return _stream([
        {
            "role": "system",
            "content": "You are a career expert specializing in matching candidate skills to job requirements.",
        },
        {
            "role": "user",
            "content": f"""Match skills from this CV to the job description requirements.

CV:
{cv_text}

Job Description:
{job_description}

Provide:

**Technical Skills to Highlight** (from CV that match the job — top 6-8)
**Soft Skills to Emphasize** (relevant to this role — top 4-5)
**Certifications or Qualifications to Feature** (if any)
**Skills Gap** (skills in the job description not evident in the CV — what to develop)

Use bullet points and be specific.""",
        },
    ])


def generate_interview_questions(cv_text: str, job_description: str):
    return _stream([
        {
            "role": "system",
            "content": "You are an experienced hiring manager and interview coach.",
        },
        {
            "role": "user",
            "content": f"""Generate likely interview questions for this candidate based on their CV and the job description.

CV:
{cv_text}

Job Description:
{job_description}

Generate 8 interview questions:
- 3 behavioral questions (STAR method — about past experiences)
- 3 technical or role-specific questions
- 1 question about a potential concern or gap in the CV
- 1 culture or motivation question

For each question add a brief tip (1-2 sentences) on how to answer using specific content from the CV.""",
        },
    ])


def generate_salary_estimate(cv_text: str, job_description: str):
    return _stream([
        {
            "role": "system",
            "content": "You are a compensation specialist with deep knowledge of salary benchmarking across industries.",
        },
        {
            "role": "user",
            "content": f"""Estimate the salary range for this role based on the job description and the candidate's CV.

CV:
{cv_text}

Job Description:
{job_description}

Provide:

**Estimated Salary Range** — give a specific range, note currency and location assumptions
**Factors Pushing Higher** — aspects of the CV that command a premium
**Factors Pushing Lower** — gaps or weaknesses that may reduce offers
**Typical Benefits** — what is usually offered for this type of role
**Negotiation Tips** — 2-3 specific tips for this candidate's situation""",
        },
    ])

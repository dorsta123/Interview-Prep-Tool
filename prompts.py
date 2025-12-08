# prompts.py

def get_skills_prompt(jd_text: str, top_k: int) -> str:
    return f"""
    You are an expert HR Tech system.
    Analyze the job description below.
    Extract the top {top_k} technical skills, the domain (1 word), seniority level, and a brief summary.
    
    JOB DESCRIPTION:
    {jd_text}
    
    Return ONLY valid JSON in this format:
    {{
        "skills": ["skill1", "skill2"...],
        "domain": "...",
        "seniority": "...",
        "summary": "..."
    }}
    """

def get_questions_prompt(role_title: str, skills: list) -> str:
    skills_str = ", ".join(skills)
    return f"""
    You are a technical interviewer.
    Generate 20 distinct interview questions for a '{role_title}' candidate.
    Focus on these skills: {skills_str}.
    
    Return ONLY valid JSON in this format:
    [
        {{"skill": "{skills[0] if skills else 'General'}", "qtype": "technical", "prompt": "..."}},
        {{"skill": "General", "qtype": "behavioral", "prompt": "..."}}
    ]
    """

# ... (Keep existing functions)

def get_answer_prompt(question_text: str) -> str:
    return f"""
    You are an expert candidate coach. 
    Provide a concise, high-quality sample answer (STAR method if behavioral, precise if technical) for this interview question:
    
    "{question_text}"
    
    Keep the answer under 150 words.
    """
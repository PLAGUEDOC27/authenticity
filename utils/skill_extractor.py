import re

SKILL_WEIGHTS = {
    "python": 10,
    "java": 8,
    "javascript": 8,
    "react": 9,
    "node": 8,
    "express": 7,
    "mysql": 7,
    "mongodb": 7,
    "postgresql": 7,
    "flask": 8,
    "django": 8,
    "aws": 9,
    "docker": 8,
    "git": 6,
    "html": 5,
    "css": 5,
    "sql": 7,
    "machine learning": 9,
    "data analysis": 8,
    "pandas": 7,
    "numpy": 7,
    "power bi": 7,
    "tableau": 7,
    "excel": 5
}


def extract_skills(text):
    if not text:
        return []

    text = text.lower()
    found = []

    for skill in SKILL_WEIGHTS:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, text):
            found.append(skill)

    return found


def get_skill_weight(skill):
    return SKILL_WEIGHTS.get(skill.lower(), 5)
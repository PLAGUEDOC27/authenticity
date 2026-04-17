import re

# Lightweight ATS skill dictionary (you can expand later)
SKILL_DB = {
    "python", "java", "c", "c++", "javascript", "html", "css",
    "flask", "django", "react", "node", "sql", "mysql",
    "mongodb", "postgresql", "aws", "docker", "kubernetes",
    "git", "linux", "machine learning", "deep learning",
    "data analysis", "pandas", "numpy", "tensorflow"
}

def extract_skills(text):
    if not text:
        return []

    text = text.lower()

    found = set()

    # match multi-word skills first
    for skill in SKILL_DB:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, text):
            found.add(skill)

    return list(found)
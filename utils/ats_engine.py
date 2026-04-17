import re

# ---------- BASIC SKILL EXTRACTOR ----------
def extract_skills(text):
    SKILL_DB = {
        "python", "java", "c++", "javascript", "react", "node", "express",
        "mysql", "mongodb", "flask", "django", "aws", "docker",
        "html", "css", "git", "rest api", "machine learning", "sql"
    }

    text = text.lower()
    found = set()

    for skill in SKILL_DB:
        if skill in text:
            found.add(skill)

    return list(found)


# ---------- ATS SCORER ----------
def compute_ats_score(jd_text, resume_text):

    jd_skills = set(extract_skills(jd_text))
    resume_skills = set(extract_skills(resume_text))

    if not jd_skills:
        return 0, [], []

    matched = list(jd_skills & resume_skills)
    missing = list(jd_skills - resume_skills)

    score = (len(matched) / len(jd_skills)) * 100

    return round(score, 2), matched, missing
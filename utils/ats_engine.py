import re
from utils.skill_extractor import extract_skills, get_skill_weight

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

    total_weight = sum(get_skill_weight(skill) for skill in jd_skills)
    matched_weight = sum(get_skill_weight(skill) for skill in matched)

    skill_score = (matched_weight / total_weight) * 100 if total_weight else 0

    jd_words = set(jd_text.lower().split())
    resume_words = set(resume_text.lower().split())

    keyword_score = (len(jd_words & resume_words) / max(len(jd_words), 1)) * 100

    length_score = min(len(resume_text) / 3000, 1) * 100

    final_score = (
        skill_score * 0.70 +
        keyword_score * 0.20 +
        length_score * 0.10
    )

    return round(final_score, 2), matched, missing

def generate_ats_explanation(score, matched, missing):

    explanation = []

    if score >= 75:
        explanation.append("Strong match for the job description.")
    elif score >= 50:
        explanation.append("Moderate match. Some improvements needed.")
    else:
        explanation.append("Weak match. Significant gaps detected.")

    if matched:
        explanation.append(
            f"Matches {len(matched)} key skills such as {', '.join(matched[:3])}."
        )

    if missing:
        explanation.append(
            f"Missing important skills like {', '.join(missing[:3])}."
        )

    if score < 40:
        explanation.append("Consider adding more relevant experience and technologies.")

    return " ".join(explanation)
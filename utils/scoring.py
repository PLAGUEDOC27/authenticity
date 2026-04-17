JD_KEYWORDS = {
    "html", "css", "javascript", "react",
    "node", "express", "mysql", "mongodb",
    "api", "git", "docker", "aws", "rest"
}

def compute_jd_score(text):
    text = (text or "").lower()

    matches = 0

    for skill in JD_KEYWORDS:
        if skill in text:
            matches += 1

    score = (matches / len(JD_KEYWORDS)) * 100
    return round(score, 2)
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def extract_skills(text):

    skills = [
        "html","css","javascript","react",
        "node.js","express","mysql","mongodb",
        "aws","docker","git","rest","api",
        "mvc","authentication" "python", "java", "react", "node", "aws",
        "docker", "mysql", "mongodb", "flask", "django", "git", "rest", "graphql"
    ]

    text = text.lower()
    return set([s for s in skills if s in text])


def compute_resume_score(jd_text, resume_text):

    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        stop_words=None
    )

    tfidf = vectorizer.fit_transform([jd_text, resume_text])
    tfidf_score = cosine_similarity(tfidf[0:1], tfidf[1:])[0][0] * 100

    jd_skills = extract_skills(jd_text)
    res_skills = extract_skills(resume_text)

    skill_score = (len(jd_skills & res_skills) / len(jd_skills)) * 100 if jd_skills else 0

    final_score = (tfidf_score * 0.4) + (skill_score * 0.6)

    return round(final_score, 2)
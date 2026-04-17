from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def check_resume_similarity(resumes):

    if len(resumes) < 2:
        return []

    texts = [r.original_text for r in resumes]

    vectorizer = TfidfVectorizer(ngram_range=(1, 2))
    tfidf = vectorizer.fit_transform(texts)

    sim_matrix = cosine_similarity(tfidf)

    similarity_pairs = []

    for i in range(len(resumes)):
        for j in range(i + 1, len(resumes)):

            score = sim_matrix[i][j] * 100

            if score > 70:   # threshold (tune later)
                similarity_pairs.append({
                    "doc1": resumes[i],
                    "doc2": resumes[j],
                    "score": round(score, 2)
                })

    return similarity_pairs
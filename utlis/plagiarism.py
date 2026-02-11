from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def calculate_plagiarism(new_doc, existing_docs):
    texts = [new_doc] + existing_docs

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(texts)

    similarity_scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])[0]

    if len(similarity_scores) == 0:
        return 0.0

    return round(max(similarity_scores) * 100, 2)

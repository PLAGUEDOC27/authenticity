from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def calculate_plagiarism(new_doc, existing_docs):
    if not existing_docs:
        return 0.0, []

    texts = [new_doc] + existing_docs

    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1,2))
    tfidf_matrix = vectorizer.fit_transform(texts)

    similarity_scores = cosine_similarity(
        tfidf_matrix[0:1], 
        tfidf_matrix[1:]
    )[0]

    report = []
    for idx, score in enumerate(similarity_scores):
        report.append({
            "document_index": idx,
            "similarity_percent": round(score * 100, 2)
        })

    max_score = round(max(similarity_scores) * 100, 2)

    return max_score, report
import re

def clean_text(text):
    text = text.lower()                     # lowercase
    text = re.sub(r'\s+', ' ', text)        # remove extra spaces
    text = re.sub(r'[^\w\s]', '', text)     # remove punctuation
    return text.strip()

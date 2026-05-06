import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def split_sentences(text):
    if not text:
        return []

    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if len(s.strip()) > 20]


def severity(score):
    if score >= 80:
        return "high"
    elif score >= 50:
        return "medium"
    return "low"


def generate_plagiarism_report(target_doc, source_docs):
    target_sentences = split_sentences(target_doc.original_text)

    source_sentences = []
    source_map = []

    for doc in source_docs:
        if doc.id == target_doc.id:
            continue

        for sent in split_sentences(doc.original_text):
            source_sentences.append(sent)
            source_map.append(doc.filename)

    if not target_sentences or not source_sentences:
        return {
            "overall_score": 0,
            "matches": []
        }

    all_sentences = target_sentences + source_sentences

    tfidf = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2)
    ).fit_transform(all_sentences)

    target_vecs = tfidf[:len(target_sentences)]
    source_vecs = tfidf[len(target_sentences):]

    matrix = cosine_similarity(target_vecs, source_vecs)

    matches = []
    scores = []

    for i, row in enumerate(matrix):
        best_index = row.argmax()
        best_score = row[best_index] * 100

        if best_score >= 35:
            scores.append(best_score)

            matches.append({
                "sentence": target_sentences[i],
                "source_sentence": source_sentences[best_index],
                "source_document": source_map[best_index],
                "score": round(best_score, 2),
                "severity": severity(best_score)
            })

    if scores:
        coverage = len(matches) / len(target_sentences)
        avg_similarity = sum(scores) / len(scores)

        overall = (coverage * 0.6 + (avg_similarity / 100) * 0.4) * 100
        overall = round(max(0, min(overall, 100)), 2)
    else:
        overall = 0

    return {
        "overall_score": overall,
        "matches": matches
    }
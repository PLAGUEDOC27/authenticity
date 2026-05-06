import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def split_sentences(text):
    sentences = re.split(r'[.!?]', text)
    return [s.strip() for s in sentences if len(s.strip()) > 10]


def check_plagiarism(new_text, documents):

    new_sentences = split_sentences(new_text)

    existing_sentences = []
    sentence_source_map = []

    for doc in documents:
        if not doc.original_text:
            continue

        for s in split_sentences(doc.original_text):
            existing_sentences.append(s)
            sentence_source_map.append(doc.filename)

    if not existing_sentences or not new_sentences:
        return 0.0, []

    all_sentences = new_sentences + existing_sentences

    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        stop_words="english"
    )

    tfidf_matrix = vectorizer.fit_transform(all_sentences)

    new_vecs = tfidf_matrix[:len(new_sentences)]
    existing_vecs = tfidf_matrix[len(new_sentences):]

    similarity_matrix = cosine_similarity(new_vecs, existing_vecs)

    report = []
    matched_sentence_ids = set()
    scores = []

    THRESHOLD = 0.35

    for i, row in enumerate(similarity_matrix):

        best_match_index = row.argmax()
        best_score = row[best_match_index]

        if best_score >= THRESHOLD:
            percent = round(best_score * 100, 2)

            report.append({
                "sentence_id": i,
                "sentence": new_sentences[i],
                "source_sentence": existing_sentences[best_match_index],
                "source_document": sentence_source_map[best_match_index],
                "similarity": percent,
                "score": percent,
                "severity": (
                    "high" if percent >= 80
                    else "medium" if percent >= 50
                    else "low"
                )
            })

            matched_sentence_ids.add(i)
            scores.append(percent)

    if not report:
        return 0.0, []

    coverage = len(matched_sentence_ids) / len(new_sentences)
    avg_similarity = sum(scores) / len(scores)

    final_score = (coverage * 0.6 + (avg_similarity / 100) * 0.4) * 100
    final_score = round(max(0, min(final_score, 100)), 2)

    return final_score, report
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

    vectorizer = TfidfVectorizer(ngram_range=(1, 2))
    tfidf_matrix = vectorizer.fit_transform(all_sentences)

    new_vecs = tfidf_matrix[:len(new_sentences)]
    existing_vecs = tfidf_matrix[len(new_sentences):]

    similarity_matrix = cosine_similarity(new_vecs, existing_vecs)

    report = []
    total_score = 0
    match_count = 0
    unique_matched_sentences = set()

    for i, row in enumerate(similarity_matrix):
        for j, score in enumerate(row):

            if score > 0.2:
                percent = score * 100

                report.append({
                    "sentence_id": i,
                    "sentence": new_sentences[i],
                    "source_document": sentence_source_map[j],
                    "similarity": round(percent, 2)
                })

                total_score += percent
                match_count += 1
                unique_matched_sentences.add(i)

    if match_count == 0:
        return 0.0, []

    coverage = len(unique_matched_sentences) / len(new_sentences)
    avg_similarity = total_score / match_count

    final_score = (coverage * 0.6 + (avg_similarity / 100) * 0.4) * 100

    final_score = round(max(0, min(final_score, 100)), 2)

    return final_score, report
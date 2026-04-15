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

    # Collect all sentences from DB
    for doc in documents:
        if not doc.original_text:
            continue

        sents = split_sentences(doc.original_text)

        for s in sents:
            existing_sentences.append(s)
            sentence_source_map.append(doc.filename)

    # 🚨 If no data
    if not existing_sentences or not new_sentences:
        return 0.0, []

    # ✅ Combine all sentences
    all_sentences = new_sentences + existing_sentences

    # ✅ ONE TF-IDF MODEL (IMPORTANT)
    vectorizer = TfidfVectorizer(ngram_range=(1, 2))
    tfidf_matrix = vectorizer.fit_transform(all_sentences)

    # Split vectors
    new_vecs = tfidf_matrix[:len(new_sentences)]
    existing_vecs = tfidf_matrix[len(new_sentences):]

    # ✅ MATRIX SIMILARITY (FAST)
    similarity_matrix = cosine_similarity(new_vecs, existing_vecs)

    report = []
    total_score = 0
    match_count = 0

    for i, row in enumerate(similarity_matrix):
        for j, score in enumerate(row):

            if score > 0.2:  # 🔥 LOWERED threshold

                percent = round(score * 100, 2)

                report.append({
                    "matched_sentence": new_sentences[i],
                    "source_document": sentence_source_map[j],
                    "similarity": percent
                })

                total_score += percent
                match_count += 1

    final_score = round(total_score / match_count, 2) if match_count else 0

    return final_score, report
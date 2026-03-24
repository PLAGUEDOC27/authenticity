import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def split_sentences(text):
    sentences = re.split(r'[.!?]', text)
    return [s.strip() for s in sentences if len(s.strip()) > 10]


def check_plagiarism(new_text, documents):

    new_sentences = split_sentences(new_text)

    report = []
    total_score = 0
    match_count = 0

    for doc in documents:

        if not doc.original_text:
            continue

        existing_sentences = split_sentences(doc.original_text)

        for s1 in new_sentences:
            for s2 in existing_sentences:

                # TF-IDF Vectorization (2 sentences at a time)
                vectorizer = TfidfVectorizer(ngram_range=(1, 2))  # unigram + bigram

                vectors = vectorizer.fit_transform([s1, s2])

                similarity_matrix = cosine_similarity(vectors[0:1], vectors[1:2])
                score = similarity_matrix[0][0]

                if score > 0.3:  # threshold (IMPORTANT)

                    percent = round(score * 100, 2)

                    report.append({
                        "matched_sentence": s1,
                        "source_document": doc.filename,
                        "similarity": percent
                    })

                    total_score += percent
                    match_count += 1

    if match_count > 0:
        final_score = total_score / match_count
    else:
        final_score = 0

    return round(final_score, 2), report
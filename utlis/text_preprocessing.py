import re
from nltk.corpus import stopwords

stop_words = set(stopwords.words("english"))

def preprocess_text(text):
    text = text.lower()
    text = re.sub(r"[^a-z\s]", "", text)

    tokens = text.split()
    tokens = [w for w in tokens if w not in stop_words]

    return " ".join(tokens)

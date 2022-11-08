from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd

with open("./stopwords.txt") as fh:
    stopwords = [line.strip() for line in fh.readlines()]


def tfidf_kw_extract(df):
    docs = df['full_text_tokens'].to_list()
    for idx, doc in enumerate(docs):
        for w in stopwords:
            doc = doc.replace(w, "")
        docs[idx] = doc
    vectorizer = TfidfVectorizer(smooth_idf=True)
    tfidf = vectorizer.fit_transform(docs)
    result = pd.DataFrame(
        tfidf.toarray(), columns=vectorizer.get_feature_names_out())
    keywords = result.sum().sort_values(ascending=False)[:20].index
    return keywords

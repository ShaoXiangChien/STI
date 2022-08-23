from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd


def tfidf_keyword_extraction(df):
    vectorizer = TfidfVectorizer(smooth_idf=True)
    tfidf = vectorizer.fit_transform(df['full_text'].to_list())
    result = pd.DataFrame(
        tfidf.toarray(), columns=vectorizer.get_feature_names_out())
    keywords = result.sum().sort_values(ascending=False)[:100].index
    return keywords

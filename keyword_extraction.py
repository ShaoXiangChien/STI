from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
from ArticutAPI import articut

# 需要先斷詞
def tfidf_keyword_extraction(df):
    vectorizer = TfidfVectorizer(smooth_idf=True)
    tfidf = vectorizer.fit_transform(
        df.title.to_list() + df.paragraph.to_list())
    result = pd.DataFrame(
        tfidf.toarray(), columns=vectorizer.get_feature_names_out())
    keywords = result.sum().sort_values(ascending=False)[:20].index
    return keywords

# 不用斷詞
def textrank_keyword_extraction(df):
    text = "".join(df.title.to_list() + df.paragraph.to_list())
    result = articut.parse(text)
    return articut.analyse.textrank(result)
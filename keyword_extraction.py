from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
from ArticutAPI import Articut
from articut import Tokenization
username = "loveyoosic4ever@gmail.com"
apikey = "=Zs6wI!L_KRO&_Ff3H5VQx3Fx145A%v"
articut = Articut(username, apikey)
# 需要先斷詞
def tfidf_keyword_extraction(df):
    tokenized_df = Tokenization(df)
    vectorizer = TfidfVectorizer(smooth_idf=True)
    tfidf = vectorizer.fit_transform(tokenized_df.title.to_list() + tokenized_df.paragraph.to_list()
        )
    result = pd.DataFrame(
        tfidf.toarray(), columns=vectorizer.get_feature_names_out())
    keywords = result.sum().sort_values(ascending=False)[:100].index
    return keywords

# 不用斷詞
def textrank_keyword_extraction(df):
    df.title = df.title.astype(str)
    df.paragraph = df.paragraph.astype(str)
    text = "".join(df.title.to_list() + df.paragraph.to_list())
    result = articut.parse(text)
    return articut.analyse.textrank(result)

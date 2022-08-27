import pandas as pd
from ckiptagger import data_utils
from ckiptagger import POS, NER, WS
from sklearn.feature_extraction.text import TfidfVectorizer


def ckip_tfidf_kw_extract(df):
    tokenized_text = df['full_text'].to_list()

    # tfidf
    vectorizer = TfidfVectorizer(smooth_idf=True)
    tfidf = vectorizer.fit_transform(tokenized_text)
    result = pd.DataFrame(
        tfidf.toarray(), columns=vectorizer.get_feature_names())
    tfidf_kwd = result.sum().sort_values(ascending=False).to_dict()

    # ckip kwd
    pos = POS('./data')
    ner = NER('./data')
    ws_result = tokenized_text
    pos_result = pos(ws_result)
    ner_result = ner(ws_result, pos_result)
    ckip_kwd = {}
    ner_tag = ['PERSON', 'WORK_OF_ART',
               'EVENT', 'FAC', 'LAW', 'PRODUCT', 'ORG']
    for news in ner_result:
        for entity in news:
            if entity[2] in ner_tag:
                if entity[3] not in ckip_kwd:
                    ckip_kwd[entity[3]] = 1
                else:
                    ckip_kwd[entity[3]] += 1

    ckip_tfidf_dt = {k: tfidf_kwd[k]
                     for k in ckip_kwd.keys() if tfidf_kwd.get(k)}
    keywords = list(
        dict(sorted(ckip_tfidf_dt.items(), key=lambda x: x[1], reverse=True)).keys())[:20]
    return keywords

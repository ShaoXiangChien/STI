from pprint import pprint
import pandas as pd
from ckiptagger import data_utils
from ckiptagger import POS, NER, WS
from sklearn.feature_extraction.text import TfidfVectorizer
from ArticutAPI import Articut

username = "yishin@gmail.com"
apikey = "UGqaeo46Aw+4HI#q2^P-pAbz!yPXxx6"
articut = Articut(username, apikey)


def kwd_extraction():
    # word segmentation
    output = pd.read_csv("../STI/萊豬 output.csv")
    output.paragraph = output.paragraph.astype(str)
    output.title = output.title.astype(str)
    tokenized_text = []
    for idx, row in output.iterrows():
        text = row.title + row.paragraph
        result = articut.parse(text)
        tokenized_text += result["result_segmentation"].split("/")

    # tfidf
    vectorizer = TfidfVectorizer(smooth_idf=True)
    tfidf = vectorizer.fit_transform(tokenized_text)
    result = pd.DataFrame(
        tfidf.toarray(), columns=vectorizer.get_feature_names())
    tfidf_kwd = result.sum().sort_values(ascending=False)[:100].index

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

    # compare
    ner_list = []
    for k, v in ckip_kwd.items():
        if k in tfidf_kwd:
            ner_list.append(k)
    return k

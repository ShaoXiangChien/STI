from pprint import pprint
import pandas as pd
from ckiptagger import data_utils

ner_tag = ['PERSON', 'WORK_OF_ART',
           'EVENT', 'FAC', 'LAW', 'PRODUCT', 'ORG']


def ckip_kw_extract(df):
    text = list(df.paragraph.astype(str)+df.title.astype(str))
    from ckiptagger import POS, NER, WS
    ws = WS("./data")
    pos = POS('./data')
    ner = NER('./data')

    ws_result = ws(text, sentence_segmentation=True,
                   segment_delimiter_set={",", "。", ":", "?", "!", ";"})
    pos_result = pos(ws_result)
    ner_result = ner(ws_result, pos_result)
    kwd_dict = {}

    for news in ner_result:
        for entity in news:
            if entity[2] in ner_tag:
                if entity[3] not in kwd_dict:
                    kwd_dict[entity[3]] = 1
                else:
                    kwd_dict[entity[3]] += 1
    keywords = list(
        dict(sorted(kwd_dict.items(), key=lambda x: x[1], reverse=True)).keys())[:20]
    return keywords

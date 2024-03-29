import pandas as pd
from ArticutAPI import Articut
from articut import Tokenization
articut = Articut(username="yishin@gmail.com",
                  apikey="UGqaeo46Aw+4HI#q2^P-pAbz!yPXxx6")

# 不用斷詞


def textrank_kw_extract(df):
    df.title = df.title.astype(str)
    df.paragraph = df.paragraph.astype(str)
    text = "".join(df.title.to_list() + df.paragraph.to_list())
    result = articut.parse(text)
    kw_result = articut.analyse.textrank(result)
    return [kw[kw.find(">") + 1:] for kw in kw_result] if kw_result else ['']

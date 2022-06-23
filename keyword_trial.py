from keyword_extraction import *
from articut import *
import pandas as pd

news = pd.read_csv("./output.csv")
textrank_kws = textrank_keyword_extraction(news)
with open("./textrank_kws.txt", 'w') as fh:
    fh.writelines([w + '\n' for w in textrank_kws])

tokenized_news = Tokenization(news)
tfidf_kws = tfidf_keyword_extraction(tokenized_news)
with open("./tfidf_kws.txt", 'w') as fh:
    fh.writelines([w + '\n' for w in tfidf_kws])
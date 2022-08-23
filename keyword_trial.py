from keyword_extraction.textrank_kw_extract import *
from articut import *
import pandas as pd

news1 = pd.read_csv("./Crawled data/普悠瑪事件 data.csv")
news1.paragraph = news1.paragraph.astype(str)
news1.title = news1.title.astype(str)
news2 = pd.read_csv("./Crawled data/龍龍老K data.csv")
news2.paragraph = news2.paragraph.astype(str)
news2.title = news2.title.astype(str)
news3 = pd.read_csv("./Crawled data/烏俄戰爭 data.csv")
news3.paragraph = news3.paragraph.astype(str)
news3.title = news3.title.astype(str)

textrank_kws = textrank_keyword_extraction(news1)
with open("./普悠瑪事件 textrank_kws.txt", 'w') as fh:
    fh.writelines([w + '\n' for w in textrank_kws])

tokenized_news = Tokenization(news1)
tfidf_kws = tfidf_keyword_extraction(tokenized_news)
with open("./普悠瑪事件 tfidf_kws.txt", 'w') as fh:
    fh.writelines([w + '\n' for w in tfidf_kws])

textrank_kws = textrank_keyword_extraction(news2)
with open("./龍龍老K textrank_kws.txt", 'w') as fh:
    fh.writelines([w + '\n' for w in textrank_kws])

tokenized_news = Tokenization(news2)
tfidf_kws = tfidf_keyword_extraction(tokenized_news)
with open("./龍龍老K tfidf_kws.txt", 'w') as fh:
    fh.writelines([w + '\n' for w in tfidf_kws])

textrank_kws = textrank_keyword_extraction(news3)
with open("./烏俄戰爭 textrank_kws.txt", 'w') as fh:
    fh.writelines([w + '\n' for w in textrank_kws])

tokenized_news = Tokenization(news3)
tfidf_kws = tfidf_keyword_extraction(tokenized_news)
with open("./烏俄戰爭 tfidf_kws.txt", 'w') as fh:
    fh.writelines([w + '\n' for w in tfidf_kws])

import json
import time
from summarization.kmeans_summarize import *
from summarization.textrank_summarize import *
from summarization.naive_summarize import *
from crawl_wiki import *

# crawl wiki
# words_to_crawl = ['聖母百花聖殿', '故宮', '開拓動漫祭', '藻礁']
text_dt = dict()
words_to_crawl = ['核四', '特斯拉', '重訓', '加密貨幣']
print("Start crawling wiki")
for word in words_to_crawl:
    text_dt[word] = cut_sentences(crawl_wiki(word))
    print(word + " information get!")
with open("./0608_wiki_text.json", 'w', encoding='utf-8') as fh:
    json.dump(text_dt, fh, ensure_ascii=False)

tic = time.perf_counter()
print("naive summarizing...")
naive_summarized = {}
for k, v in text_dt.items():
    naive_summarized[k] = naive_summarize(v.copy(), word_limit=300)
toc = time.perf_counter()
print(f"naive_summarization complete in {toc - tic:0.4f} seconds")

with open("./naive_summary.json", 'w', encoding='utf-8') as fh:
    json.dump(naive_summarized, fh)

tic = time.perf_counter()
print("kmeans summarizing...")
kmeans_summarized = {}
for k, v in text_dt.items():
    kmeans_summarized[k] = kmeans_summarize(v.copy(), word_limit=300)
toc = time.perf_counter()
print(f"kmeans_summarization complete in {toc - tic:0.4f} seconds")

with open("./kmeans_summary.json", 'w', encoding='utf-8') as fh:
    json.dump(kmeans_summarized, fh, ensure_ascii=False)

tic = time.perf_counter()
print("textrank summarizing...")
textrank_summarized = {}
for k, v in text_dt.items():
    textrank_summarized[k] = textrank_summarize(v.copy(), word_limit=300)
toc = time.perf_counter()
print(f"textrank_summarization complete in {toc - tic:0.4f} seconds")

with open("./textrank_summary.json", 'w', encoding='utf-8') as fh:
    json.dump(textrank_summarized, fh, ensure_ascii=False)

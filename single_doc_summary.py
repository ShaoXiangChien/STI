from articut import *
from crawl_wiki import *
from metrics import *
from summarization.naive_summarize import *
# from summarization.kmeans_summarize import *
from openai_services import *
from summarization.azure_summarize import *


def summarize(document):
    summary = {}
    result = articut.parse(
        document, level="lv2")
    try:
        tokenized_document = result["result_segmentation"].replace("/", " ")
    except:
        tokenized_document = "empty"

    sentences = cut_sentences(document)
    tokenized_sentences = cut_sentences(tokenized_document)

    summary['naive'] = naive_summarize(sentences, tokenized_sentences)
    # summary['kmeans'] = kmeans_summarize(tokenized_sentences)
    summary['openai'] = summarize(document)
    summary['azure_language_service'] = azure_summarize([document])

    return summary


def cut_sentences(content):
    end_flag = ['?', '!', '？', '！', '。', '…']

    content_len = len(content)
    sentences = []
    tmp_char = ''
    for idx, char in enumerate(content):
        tmp_char += char

        if (idx + 1) == content_len:
            sentences.append(tmp_char)
            break

        if char in end_flag:
            next_idx = idx + 1
            if not content[next_idx] in end_flag:
                sentences.append(tmp_char)
                tmp_char = ''

    return sentences


if __name__ == "__main__":
    with open("./topics.txt") as fh:
        topics = [line.strip() for line in fh.readlines()]

    for topic in topics:
        print(f"Start processing {topic}")
        doc = crawl_wiki(topic)
        print("wiki crawled")
        summaries = summarize(doc)

        for k, v in summaries.items():
            score = summary_f1_eval(v)
            v += f"f1 score: {score:.2f}"
            with open(f"./Experiments/{topic}/{k}_wiki_summary.txt", 'w') as fh:
                fh.write(v)
            print(f"{k}: {score:.2f}")

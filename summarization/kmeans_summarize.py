import torch
import pandas as pd
import numpy as np
import json
from sentence_transformers import SentenceTransformer
from sklearn.metrics import pairwise_distances_argmin_min
from sklearn.cluster import KMeans

PRETRAINED_MODEL_NAME = "paraphrase-xlm-r-multilingual-v1"
model = SentenceTransformer(PRETRAINED_MODEL_NAME)


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


def kmeans_summarize(sentences, number_of_clusters=0, word_limit=200):
    if number_of_clusters <= 0:
        number_of_clusters = int(np.ceil(len(sentences)**0.6))
    sentence_embeddings = model.encode(sentences)
    kmeans = KMeans(n_clusters=number_of_clusters)
    kmeans = kmeans.fit(sentence_embeddings)
    n_clusters = number_of_clusters
    avg = []
    for j in range(n_clusters):
        idx = np.where(kmeans.labels_ == j)[0]
        avg.append(np.mean(idx))
    closest, _ = pairwise_distances_argmin_min(
        kmeans.cluster_centers_, sentence_embeddings)
    ordering = sorted(range(n_clusters), key=lambda k: avg[k])
    result += [sentences[closest[idx]] for idx in ordering]
    word_count = 0
    sentence_count = len(result)
    for idx, res in enumerate(result):
        word_count += len(res)
        if word_count >= word_limit:
            sentence_count = idx + 1 if idx < sentence_count else idx
            break

    summary = ' '.join(result[:sentence_count])
    return summary

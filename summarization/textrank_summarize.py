import tensorflow_hub as hub
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import networkx as nx
import ssl
import streamlit as st

ssl._create_default_https_context = ssl._create_unverified_context
# try:
embed = hub.load(
    "./universal-sentence-encoder-multilingual_3")
# except:
#     embed = hub.load(
#         "https://tfhub.dev/google/universal-sentence-encoder-multilingual/3")
#     embed.save("./universal-sentence-encoder-multilingual_3")


# @st.experimental_memo(suppress_st_warning=True)
def textrank_summarize(sentences, word_limit=200):
    # result = [sentences[0]]
    # sentences.pop(0)
    # word_limit -= len(result[0])
    embeddings = embed(sentences)
    # generate cosine similarity matrix
    sim_matrix = cosine_similarity(embeddings)
    # create graph and generate scores from pagerank algorithms
    nx_graph = nx.from_numpy_array(sim_matrix)
    scores = nx.pagerank(nx_graph)
    ranked_sentences = sorted(
        ((scores[i], s) for i, s in enumerate(sentences)), reverse=True)

    result = [i[1] for i in ranked_sentences]
    sentence_count = len(result)
    word_count = 0
    for idx, res in enumerate(result):
        word_count += len(res)
        if word_count >= word_limit:
            sentence_count = idx + 1 if idx < sentence_count else idx
            break
    summary = " ".join(result[:sentence_count])
    return summary

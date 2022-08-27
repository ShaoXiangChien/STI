import tensorflow_hub as hub
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import networkx as nx

embed = hub.load(
    "https://tfhub.dev/google/universal-sentence-encoder-multilingual/3")


def summarize(sentences):
    embeddings = embed(sentences)
    # generate cosine similarity matrix
    sim_matrix = cosine_similarity(embeddings)
    # create graph and generate scores from pagerank algorithms
    nx_graph = nx.from_numpy_array(sim_matrix)
    scores = nx.pagerank(nx_graph)
    ranked_sentences = sorted(
        ((scores[i], s) for i, s in enumerate(sentences)), reverse=True)

    num_of_sentences = 5

    summary = " ".join([i[1] for i in ranked_sentences[:num_of_sentences]])
    return summary

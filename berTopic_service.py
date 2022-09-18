from bertopic import BERTopic


def topic_modeling(docs: list):
    model = BERTopic(language="Chinese (Traditional)",
                     calculate_probabilities=True,
                     verbose=True)
    topics, probs = model.fit_transform(docs)
    topic_kws = {}
    for k, v in model.get_topics().items():
        topic_kws[k] = [kw[0] for kw in v]
    return topics, topic_kws

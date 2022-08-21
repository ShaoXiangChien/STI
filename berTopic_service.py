from bertopic import BERTopic


def topic_modeling(df):
    model = BERTopic(language="Chinese (Traditional)",
                     calculate_probabilities=True,
                     verbose=True)
    df['full_tokens'] = df.apply(
        lambda row: row['title_tokens'] + " " + row['paragraph_tokens'], axis=1)
    docs = df['full_tokens'].to_list()
    topics, probs = model.fit_transform(docs)
    df['topic'] = topics
    topic_kws = {}
    for k, v in model.get_topics().items():
        topic_kws[k] = [kw[0] for kw in v]
    return df, topic_kws

import pandas as pd
from bertopic import BERTopic
from hdbscan import HDBSCAN
from umap import UMAP

#input paired_df 為 find_time() 後的 Time event pair dataframe

def Bertopic_Clustering(paired_df: pd.DataFrame):
    paired_df = paired_df[paired_df.Time.str.len()>8]
    docs=paired_df["Event"].tolist()
    umap_model = UMAP(n_neighbors=10, n_components=25, min_dist=0.1, metric='cosine')
    hdbscan_model = HDBSCAN(min_cluster_size=5, metric='euclidean', cluster_selection_method='eom', prediction_data=True ,min_samples=10)
    topic_model = BERTopic(language='multilingual',umap_model=umap_model,hdbscan_model=hdbscan_model)
    topics, probs = topic_model.fit_transform(docs)

    representative_list=[]
    for i,event in topic_model.get_representative_docs().items():
        representative_list.append(event[0])
        final_topics=pd.DataFrame({
            "Time":[],
            "Event":[]
        })

    for event in representative_list:
        final_topics=final_topics.append({
            "Time":paired_df[paired_df["Event"]==event].iat[0,0],
            "Event":event
        },ignore_index=True)
    
    final_topics=final_topics.sort_values(by=["Time"])
    return final_topics


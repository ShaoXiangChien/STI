import pandas as pd
import time
import streamlit as st
import json
import trafilatura
from trafilatura.settings import use_config
from stqdm import stqdm
from bertopic import BERTopic
from hdbscan import HDBSCAN
from umap import UMAP

# import self-defined modules
from data_collection import *
from articut import *
from crawl_wiki import *
from clean_df import *
from metrics import *
from anomaly_detection import *
from keyword_extraction.tfidf_kw_extract import tfidf_kw_extract as kw_extract
from crawl_wiki import crawl_wiki
from summarization.azure_summarize import azure_summarize_wiki

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



@st.cache
def timeline_generate(df):
    time_df, fig, anomalies = detect_anomaly_from_df(
                df, 90)
    time_df = time_df[time_df.Time.isin(anomalies)]
    docs=time_df["Event"].tolist()
    umap_model = UMAP(n_neighbors=10, n_components=25, min_dist=0.1, metric='cosine')
    hdbscan_model = HDBSCAN(min_cluster_size=5, metric='euclidean', cluster_selection_method='eom', prediction_data=True)
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
            "Time":time_df[time_df["Event"]==event].iat[0,0],
            "Event":event
        },ignore_index=True)
    return final_topics


if __name__ == '__main__':
    st.title("時事圖文懶人包自動生成器")
    newconfig = use_config("myfile.cfg")
    st.session_state['event'] = st.text_input("請輸入您想搜尋的事件", "萊豬")
    data_source = st.selectbox("資料來源", ['Crawl Now', 'Upload File'])

    if data_source == "Crawl Now":
        if st.checkbox("開始爬取"):
            st.write('資料蒐集進行中...')
            st.session_state['news_df'] = pd.DataFrame()
            tic = time.perf_counter()
            news = collect_data(st.session_state['event'])
            num = len(news)
            toc = time.perf_counter()
            st.success(
                f"在{toc - tic:0.4f}秒後搜集了{num}筆可用的資料")
            if num != 0:
                source_dt = collect_target_news(news)
                for k, v in source_dt.items():
                    st.write("Parsing content from " + k)
                    for piece in stqdm(v):
                        try:
                            content = trafilatura.fetch_url(
                                piece['link'])
                            extracted = trafilatura.extract(
                                content, config=newconfig) if content else []
                            article_contents = ''.join(
                                extracted) if extracted else ''
                            if article_contents != "":
                                print("Article extracted")
                            else:
                                print("Fail to extract article")
                            piece['article'] = article_contents
                        except Exception as e:
                            print(e)
                        try:
                            row = pd.DataFrame(parse_content(
                                k, piece), index=[0])
                            st.session_state['news_df'] = pd.concat(
                                [st.session_state['news_df'], row], ignore_index=True, axis=0)
                        except Exception as e:
                            print(e)
                            continue
                    source_dt[k] = len(v)
                st.session_state['news_df'].to_csv(f"./Experiments/{st.session_state['event']}_news.csv", index=False,
                                                    encoding="utf-8-sig")
                st.session_state['news_df'] = clean_df(
                    st.session_state['news_df'])
                st.write("data cleaning finished")
                st.session_state['news_df'] = Tokenization(
                    st.session_state['news_df'])
                st.write("tokenization finished")
                st.session_state['news_df']['full_text'] = st.session_state['news_df'].apply(lambda x: str(
                    x['title']) + " " + str(x['paragraph']), axis=1)
                st.session_state['news_df']['full_text_tokens'] = st.session_state['news_df'].apply(lambda x: str(
                    x['title_tokens']) + " " + str(x['paragraph_tokens']), axis=1)
                st.session_state['news_df'].to_csv(f"./Experiments/{st.session_state['event']}/news.csv", index=False,
                                                    encoding="utf-8-sig")
                st.session_state['data collected'] = True
    else:
        uploaded_file = st.file_uploader("Choose a file")
        if uploaded_file is not None:
            news_df = pd.read_csv(uploaded_file)
            with st.form("Read file form"):
                clean_required = st.checkbox("Require data cleaning")
                tokenization_required = st.checkbox(
                    "Require Tokenization")
                submitted = st.form_submit_button("Submit")

            if submitted:
                if clean_required:
                    news_df = clean_df(news_df)

                if tokenization_required:
                    news_df['title'] = news_df['title'].astype(str)
                    news_df['paragraph'] = news_df['paragraph'].astype(
                        str)
                    news_df = Tokenization(news_df)
                    news_df['full_text'] = news_df.apply(lambda x: str(
                        x['title']) + " " + str(x['paragraph']), axis=1)
                    news_df['full_text_tokens'] = news_df.apply(lambda x: str(
                        x['title_tokens']) + " " + str(x['paragraph_tokens']), axis=1)
                st.session_state['news_df'] = news_df
                st.session_state['news_df'].to_csv(
                    f"./Experiments/{st.session_state['event']}/news.csv", index=False)
                st.session_state['data collected'] = True
        else:
            st.warning("The uploaded file is empty")

    if st.session_state.get('data collected'):
        keywords = kw_extract(st.session_state['news_df'])
        with st.form("choose keywords"):
            chosen_keywords = st.multiselect("以下為此事件的關鍵字，選擇你想了解的字詞", keywords)
            kw_submitted = st.form_submit_button("確認")
        
            if kw_submitted:
                kw_wiki = [crawl_wiki(k) for k in stqdm(chosen_keywords)]
                kw_wiki_summaries = {chosen_keywords[idx]: wiki for idx, wiki in enumerate(azure_summarize_wiki(kw_wiki))}
                n = len(kw_wiki_summaries)
                for i in range(0, n, 3):
                    cols = st.columns(3)
                    for j in range(3):
                        if i + j >= n:
                            break
                        kw = chosen_keywords[i + j]
                        cols[(i + j) % 3].markdown(f"""
                        ## {kw}
                        {kw_wiki_summaries[kw]}
                        """)
            
        timeline_df = timeline_generate(st.session_state['news_df'])
        
        # time_df.to_csv(f"./Experiments/{event}/time_df.csv", index=False)

            




       
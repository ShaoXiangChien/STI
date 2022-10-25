import pandas as pd
from pprint import pprint
import time
import streamlit as st
from datetime import datetime as dt
from streamlit_timeline import timeline
import json
import trafilatura
from trafilatura.settings import use_config
from stqdm import stqdm
import random


# import self-defined modules
from data_collection import *
from articut import *
from crawl_wiki import *
from clean_df import *
from metrics import *
from anomaly_detection import *
from main_functions import *
# from berTopic_service import *
from find_time import *

KW_METHODS = ['tfidf', 'textrank',
              'azure language service', 'ckip', 'ckip_tfidf', 'openai']
SM_METHODS = ['naive', 'kmeans', 'textrank',
              'openai', "azure_language_service"]
start_tokenize = False
start_kw_extract = False
start_bg_search = False
start_summary = False
event = ""


@st.cache
def anomaly_detect(time_df):
    return detect_anomaly_from_df(
        time_df, 95)


if __name__ == '__main__':
    st.title("時事圖文懶人包自動生成器")
    newconfig = use_config("myfile.cfg")
    mode = st.selectbox("Select a mode", ["Experiment", "Live Demo"])
    if mode == "Experiment":
        stage = st.sidebar.selectbox("Select the task you want to perform", [
            "Data Collection", "Keyword Extraction", "Summarization", "Timeline Generation"])
        if stage == "Data Collection":
            event = st.text_input("請輸入您想搜尋的事件", "萊豬")
            st.session_state['event'] = event
            st.header("資料蒐集與爬取")
            data_source = st.selectbox("資料來源", ['Crawl Now', 'Upload File'])
            if data_source == "Crawl Now":
                if st.checkbox("開始爬取"):
                    st.write('資料蒐集進行中...')
                    st.session_state['news_df'] = pd.DataFrame()
                    tic = time.perf_counter()
                    news = collect_data(event)
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
                                    print(piece)
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
                        st.session_state['news_df'].to_csv(f"./Experiments/{st.session_state['event']}/news.csv", index=False,
                                                           encoding="utf-8-sig")
                        st.subheader("資料來源")
                        st.write(source_dt)
                        st.session_state['news_df'] = clean_df(
                            st.session_state['news_df'])
                        st.session_state['news_df'] = Tokenization(
                            st.session_state['news_df'])
                        st.session_state['news_df']['full_text'] = st.session_state['news_df'].apply(lambda x: str(
                            x['title']) + " " + str(x['paragraph']), axis=1)
                        st.session_state['news_df']['full_text_tokens'] = st.session_state['news_df'].apply(lambda x: str(
                            x['title_tokens']) + " " + str(x['paragraph_tokens']), axis=1)
                        st.session_state['news_df'].to_csv(f"./Experiments/{st.session_state['event']}/news.csv", index=False,
                                                           encoding="utf-8-sig")
                        st.write(st.session_state['news_df'])
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
                        st.write(news_df)
                else:
                    st.warning("The uploaded file is empty")

        elif stage == "Keyword Extraction":
            st.header("關鍵字萃取方法測試")
            news_df = st.session_state['news_df']
            if news_df.shape[0] == 0:
                st.warning("news_df is empty, please collect data first.")
                st.write(news_df)
            else:
                with st.form("keyword form"):
                    ans = st.text_input("輸入自訂關鍵字答案，請用空白間隔開").split(" ")
                    kw_method = st.selectbox("Select a method", KW_METHODS)
                    submitted = st.form_submit_button("Submit")

                if submitted:
                    st.write("Extracting")
                    keywords = keyword_extract(kw_method, news_df)
                    st.session_state['keywords'] = keywords
                    with open(f"./Experiments/{st.session_state['event']}/{kw_method}_keywords.txt", 'w') as fh:
                        fh.writelines((kw + "\n" for kw in keywords))
                    if len(keywords) != 1:
                        map_score = keyword_map_eval(ans, keywords)
                        hits, precision = keyword_precision_eval(ans, keywords)

                        st.write("Extraction complete")
                        st.write(f"Expected Output: {' '.join(ans)}")
                        st.write(f"Actual Output: {' '.join(keywords)}")
                        st.write(f"Precision: {precision:.2f}")
                        st.write(f"Num of Hit: {hits}")
                        st.write(f"MAP Score: {map_score:.2f}")
                        with open(f"./Experiments/{st.session_state['event']}/{kw_method}_scores.json", 'w') as fh:
                            json.dump({
                                "precision": precision,
                                "hit": hits,
                                "map": map_score
                            }, fh)
                    else:
                        st.write(f"Extracted Keywords: {keywords}")
        elif stage == "Summarization":
            st.header("摘要方法測試")
            if st.session_state['news_df'].shape[0] == 0:
                st.warning("news_df is empty, please collect data first.")
            else:
                with st.form("summary_form"):
                    ans = st.text_area("輸入標準答案")
                    sm_method = st.selectbox("Select a method", SM_METHODS)
                    submit = st.form_submit_button("Submit")

                if submit:
                    summary = summarize(
                        sm_method, st.session_state['news_df'] if st.session_state['news_df'].shape[0] != 0 else "").replace("\n", "").replace(" ", "")
                    st.write(summary)
                    f1_score = summary_f1_eval(
                        summary, ans.replace("\n", "").replace(" ", ""))
                    st.write(f"f1 score: {f1_score}\n")
                    summary = f"f1 score: {f1_score}\n" + summary
                    with open(f"./Experiments/{st.session_state['event']}/{sm_method}_summary.txt", "w") as fh:
                        fh.write(summary)

        elif stage == "Timeline Generation":
            st.header("事件時間軸")
            time_df = find_time(st.session_state['news_df'])
            ft = time_df['Time'].apply(lambda x: len(x) > 5)
            time_df = time_df[ft]
            time_df['timestamp'] = time_df['Time'].apply(
                lambda x: str_to_time(str(x)))
            time_df.to_csv(
                f"./Experiments/{event}/time_df.csv", index=False)
            grouping_method = st.selectbox(
                "Choose a method", ["Anomaly Detector", "BerTopic"])
            if grouping_method == "Anomaly Detector":
                fig, anomalies = anomaly_detect(time_df)
                timeline_data = generate_timeline(time_df, anomalies)
                timeline(timeline_data, height=400)

            # elif grouping_method == "BerTopic":
            #     topics, topic_kws = topic_modeling(time_df['Event'].to_list())
            #     time_df['topic'] = topics

            # Evaluation
            reference = [("d1", "s1")]
            performance = alignment_rouge(reference, time_df)

    elif mode == "Live Demo":
        pass
        # event = st.text_input("請輸入您想搜尋的事件", "萊豬")
        # st.header("資料蒐集與爬取")
        # n = st.number_input(
        #     "欲爬取的google搜尋結果頁數", 0, 1000, value=2)
        # if st.checkbox("開始爬取"):
        #     st.write('資料蒐集進行中...')
        #     tic = time.perf_counter()
        #     news = collect_data(event, n)
        #     with open('./raw_news_{}.json'.format(event), 'w', encoding='utf-8') as fh:
        #         json.dump(news, fh, ensure_ascii=False)
        #     num = len(news)
        #     toc = time.perf_counter()
        #     st.success(
        #         f"在{toc - tic:0.4f}秒後搜集了{num}筆可用的資料")
        #     if num != 0:
        #         source_dt = collect_target_news(news)
        #         news_df = pd.DataFrame()
        #         for k, v in news.items():
        #             source_dt[k] = len(v)
        #             for piece in v:
        #                 try:
        #                     row = pd.DataFrame(parse_content(
        #                         k, piece), index=[0])
        #                     news_df = pd.concat(
        #                         [news_df, row], ignore_index=True, axis=0)
        #                 except:
        #                     continue
        #         st.subheader("資料來源")
        #         st.write(source_dt)
        #         news_df.to_csv('output.csv', index=False, encoding="utf-8-sig")
        #     else:
        #         news_df = pd.read_csv("../scraper/filtered_data.csv")
        #         st.write(news_df.source.value_counts())
        #     # sentences = []
        #     # for paragraph in news_df[news_df.paragraph.notnull()].paragraph.apply(lambda x: cut_sentences(x)):
        #     #     sentences += paragraph
        #     start_kw_extract = True
        # # news_df = pd.read_csv("./output.csv")
        # st.write(news_df)

        # st.header("關鍵字萃取")
        # if start_kw_extract:
        #     full_text = ' '.join(news_df.paragraph.fillna(
        #         "").to_list() + news_df.title.fillna("").to_list())
        #     keywords = keyword_extract(kw_method, full_text)
        #     st.write(keywords)
        #     with open(f"./{kw_method}_keywords.txt", 'w') as fh:
        #         fh.writelines((kw + '\n' for kw in keywords))
        #     start_bg_search = True

    # st.header("背景資料")
    # if start_bg_search:
    #     # with open("./background_original_text.json", encoding='utf-8') as fh:
    #     #     original_text = json.load(fh)
    #     original_text = {}
    #     background_dt = {}
    #     for kw in selected_keywords[:5]:
    #         content = crawl_wiki(kw)
    #         original_text[kw] = content
    #     with open("background_original_text.json", 'w', encoding='utf-8') as fh:
    #         json.dump(original_text, fh, ensure_ascii=False)
    #     for k, v in original_text.items():
    #         sentences = cut_sentences(v)
    #         try:
    #             summary = textrank_summarize(sentences, 300)
    #         except:
    #             summary = v
    #         background_dt[k] = summary

    #     with open("background.json", 'w', encoding='utf-8') as fh:
    #         json.dump(background_dt, fh, ensure_ascii=False)
    #     # with open("./background.json", encoding='utf-8') as fh:
    #     #     background_dt = json.load(fh)
    #     for k, v in background_dt.items():
    #         st.subheader(k)
    #         st.write(v)

    # st.header("文本摘要")
    # if start_summary:
    #     summary = summarize(sentences).replace(" ", "")
    #     st.subheader("摘要結果")
    #     st.write(summary)
    #     with open("./news_summary.txt", 'w') as fh:
    #         fh.write(summary)

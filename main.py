import pandas as pd
from pprint import pprint
import time
import streamlit as st
import json

# import self-defined modules
from data_collection import *
from articut import *
from crawl_wiki import *
# from naive_summarize import *
# from kmeans_summarize import *
from summarization.textrank_summarize import *


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


if __name__ == '__main__':
    start_tokenize = False
    start_kw_extract = False
    start_bg_search = False
    start_summary = False

    st.title("時事圖文懶人包自動生成器")
    event = st.text_input("請輸入您想搜尋的事件", "萊豬")
    st.header("資料蒐集與爬取")
    n = st.number_input(
        "欲爬取的google搜尋結果頁數", 0, 1000, value=2)
    if st.checkbox("開始爬取"):
        st.write('資料蒐集進行中...')
        tic = time.perf_counter()
        news, num = collect_data(event, n)
        with open('./raw_news_{}.json'.format(event), 'w', encoding='utf-8') as fh:
            json.dump(news, fh, ensure_ascii=False)

        toc = time.perf_counter()
        st.success(
            f"在{toc - tic:0.4f}秒後搜集了{num}筆可用的資料")
        if num != 0:
            news_df = pd.DataFrame()
            source_dt = {}
            for k, v in news.items():
                source_dt[k] = len(v)
                for piece in v:
                    try:
                        row = pd.DataFrame(parse_content(
                            k, piece), index=[0])
                        news_df = pd.concat([news_df, row], ignore_index=True)
                    except:
                        continue
            st.subheader("資料來源")
            st.write(source_dt)
            news_df.to_csv('output.csv', index=False, encoding="utf-8-sig")
        else:
            news_df = pd.read_csv("../scraper/filtered_data.csv")
            st.write(news_df.source.value_counts())
        # sentences = []
        # for paragraph in news_df[news_df.paragraph.notnull()].paragraph.apply(lambda x: cut_sentences(x)):
        #     sentences += paragraph
        start_kw_extract = True
    # news_df = pd.read_csv("./output.csv")
    # st.write(news_df)
    # start_kw_extract = True

    # st.header("斷詞")
    # if start_tokenize:
    #     news_df = Tokenization(news_df)
    #     st.success("斷詞完成")
    #     start_kw_extract = True

    st.header("關鍵字萃取")
    if start_kw_extract:
        selected_keywords = []
        kw_tags = ['nouny', 'KNOWLEDGE', 'person']
        full_text = ' '.join(news_df.paragraph.fillna(
            "").to_list() + news_df.title.fillna("").to_list())
        keywords = keyword_extract(full_text)
        for kw in keywords:
            found = False
            for tag in kw_tags:
                if tag in kw:
                    found = True
                    break
            if found:
                selected_keywords.append(kw[kw.find('>')+1:])

        st.write(selected_keywords)
        with open("./textrank_keywords.txt", 'w') as fh:
            fh.writelines((kw + '\n' for kw in keywords))

        with open("./selected_keywords.txt", 'w') as fh:
            fh.writelines((kw + '\n' for kw in selected_keywords))
        start_bg_search = True

    # with open("./keywords.txt") as fh:
    #     keywords = [line.strip() for line in fh.readlines()]
    # with open("./selected_keywords.txt") as fh:
    #     selected_keywords = [line.strip() for line in fh.readlines()]

    st.header("背景資料")
    if start_bg_search:
        # with open("./background_original_text.json", encoding='utf-8') as fh:
        #     original_text = json.load(fh)
        original_text = {}
        background_dt = {}
        for kw in selected_keywords[:5]:
            content = crawl_wiki(kw)
            original_text[kw] = content
        with open("background_original_text.json", 'w', encoding='utf-8') as fh:
            json.dump(original_text, fh, ensure_ascii=False)
        for k, v in original_text.items():
            sentences = cut_sentences(v)
            try:
                summary = textrank_summarize(sentences, 300)
            except:
                summary = v
            background_dt[k] = summary

        with open("background.json", 'w', encoding='utf-8') as fh:
            json.dump(background_dt, fh, ensure_ascii=False)
        # with open("./background.json", encoding='utf-8') as fh:
        #     background_dt = json.load(fh)
        for k, v in background_dt.items():
            st.subheader(k)
            st.write(v)

    # st.header("文本摘要")
    # if start_summary:
    #     summary = summarize(sentences).replace(" ", "")
    #     st.subheader("摘要結果")
    #     st.write(summary)
    #     with open("./news_summary.txt", 'w') as fh:
    #         fh.write(summary)

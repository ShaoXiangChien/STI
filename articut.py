from turtle import title
from ArticutAPI import Articut
from pprint import pprint
import sqlite3
from numpy import dtype
import pandas as pd
from requests import head
import streamlit as st
"""
conn=sqlite3.connect("./News.db")
cursor = conn.cursor()
inputdataframe=pd.read_sql("SELECT * FROM News",conn)
inputdataframe=inputdataframe.replace("","NA")
"""
username = "loveyoosic4ever@gmail.com"
apikey = "=Zs6wI!L_KRO&_Ff3H5VQx3Fx145A%v"
articut = Articut(username, apikey)
# inputdataframe = pd.read_csv("output.csv")


@st.experimental_memo(suppress_st_warning=True)
def Tokenization(df):
    # 這裡填入您在 https://api.droidtown.co 使用的帳號 email。若使用空字串，則預設使用每小時 2000 字的公用額度。
    # 這裡填入您在 https://api.droidtown.co 登入後取得的 api Key。若使用空字串，則預設使用每小時 2000 字的公用額度。

    # titles = []
    # for sentence in df["title"]:
    #     result = articut.parse(sentence)
    #     contentwordlist = articut.getContentWordLIST(result)
    #     contentword = ""
    #     for a in contentwordlist:
    #         for word in a:
    #             contentword += word[-1]
    #             contentword += "/"
    #     contentword = contentword[:-1]
    #     titles.append(contentword)
    titles = []
    for sentence in df["title"]:
        result = articut.parse(
            sentence, level="lv2")
        try:
            titles.append(result["result_segmentation"].replace("/", " "))
        except:
            titles.append('')
    df["title_tokens"] = titles

    # paragraphs = []
    # for sentence in df["paragraph"]:
    #     result = articut.parse(sentence)
    #     contentwordlist = articut.getContentWordLIST(result)
    #     contentword = ""
    #     for a in contentwordlist:
    #         for word in a:
    #             contentword += word[-1]
    #             contentword += "/"
    #     contentword = contentword[:-1]
    #     paragraphs.append(contentword)
    paragraphs = []
    for sentence in df["paragraph"]:
        result = articut.parse(
            sentence, level="lv2")
        try:
            paragraphs.append(result["result_segmentation"].replace("/", " "))
        except:
            paragraphs.append('')

    df["paragraph_tokens"] = paragraphs

    return df

# test
# outputdataframe=Tokenization(inputdataframe)
# outputdataframe.to_csv("Covid_Tokenized.csv",encoding='utf_8_sig')


def keyword_extract(text):
    result = articut.parse(text)
    return articut.analyse.textrank(result)

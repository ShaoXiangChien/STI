from turtle import title
from ArticutAPI import Articut
from pprint import pprint
import sqlite3
from numpy import dtype
import pandas as pd
from requests import head

"""
conn=sqlite3.connect("./News.db")
cursor = conn.cursor()
inputdataframe=pd.read_sql("SELECT * FROM News",conn)
inputdataframe=inputdataframe.replace("","NA")
"""

inputdataframe=pd.read_csv("output.csv")

def Tokenization(Dataframe):
    username = "loveyoosic4ever@gmail.com" #這裡填入您在 https://api.droidtown.co 使用的帳號 email。若使用空字串，則預設使用每小時 2000 字的公用額度。
    apikey   = "=Zs6wI!L_KRO&_Ff3H5VQx3Fx145A%v" #這裡填入您在 https://api.droidtown.co 登入後取得的 api Key。若使用空字串，則預設使用每小時 2000 字的公用額度。
    articut = Articut(username, apikey)
    titles=[]
    for sentence in Dataframe["title"]:
        result=articut.parse(sentence)
        contentwordlist=articut.getContentWordLIST(result)
        contentword=""
        for a in contentwordlist:
            for word in a:
                contentword+=word[-1]
                contentword+="/"
        contentword=contentword[:-1]
        titles.append(contentword)
    Dataframe["title"]=titles
    
    paragraphs=[]
    for sentence in Dataframe["paragraph"]:
        result=articut.parse(sentence)
        contentwordlist=articut.getContentWordLIST(result)
        contentword=""
        for a in contentwordlist:
            for word in a:
                contentword+=word[-1]
                contentword+="/"
        contentword=contentword[:-1]
        paragraphs.append(contentword)
    Dataframe["paragraph"]=paragraphs
    
    return Dataframe

# test
outputdataframe=Tokenization(inputdataframe)
outputdataframe.to_csv("Covid_Tokenized.csv",encoding='utf_8_sig')

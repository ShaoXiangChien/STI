from find_time import *
from berTopic_service import *
import pandas as pd
import re
import arrow

df= pd.read_csv("C:/Users/Howard/Desktop/CS＿project/STI/Experiments/龍龍老K/news.csv")

event_pair=find_time(df)
timeline=Bertopic_Clustering(event_pair)
print(timeline)


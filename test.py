from find_time import *
import pandas as pd

f=pd.read_csv("./Experiments/龍龍老K/news.csv")
output = find_time(f,tokenized=True)

output.to_csv("./Experiments/龍龍老K/time_events.csv",encoding="utf-8-sig",index=False)

from pprint import pprint
import arrow
import pandas as pd
import re
from clean_df import *

f=pd.read_csv('萊豬 output.csv',encoding='utf-8-sig')
f=clean_df(f)
f.to_csv('萊豬 cleaned.csv',encoding='utf-8-sig',index=False)
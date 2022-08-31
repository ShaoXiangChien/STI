from datetime import date
from pickle import TRUE
from pprint import pprint
import pandas as pd
import re
from clean_df import *


def chineses_to_num(input: str):
    translate_table = {
        '零': 0,
        '一': 1,
        '二': 2,
        '三': 3,
        '四': 4,
        '五': 5,
        '六': 6,
        '七': 7,
        '八': 8,
        '九': 9,
        '十': 10
    }
    print
    # 結果
    result_str = ''
    #暫存數字
    tmp_num=0
    idx = 0
    while idx < len(input):
        if translate_table.get(input[idx]) is not None:
            current_word = translate_table.get(input[idx])
            if current_word == 10:
                if tmp_num == 0:
                    tmp_num = 1
                if translate_table.get(input[idx+1]) is None:
                    tmp_num*=10
            else:
                tmp_num=tmp_num*10+current_word

        else:
            if tmp_num != 0:
                result_str += str(tmp_num)
                tmp_num = 0
            result_str += input[idx]
        idx += 1
    if tmp_num != 0:
        result_str += str(tmp_num)
    return result_str
    

from pprint import pprint
from unicodedata import numeric
import pandas as pd
from clean_df import *
import arrow
from anomaly_detection import *


def chineses_to_num(input: str):
    translate_table = {
        '零': 0,
        '○': 0,
        '一': 1,
        '二': 2,
        '三': 3,
        '四': 4,
        '五': 5,
        '六': 6,
        '七': 7,
        '八': 8,
        '九': 9,
        '十': 10,
        '百': 100
    }
    print
    # 結果
    result_str = ''
    # 暫存數字
    tmp_num = 0
    idx = 0
    while idx < len(input):
        if translate_table.get(input[idx]) is not None:
            current_word = translate_table.get(input[idx])
            if current_word == 10:
                if tmp_num == 0:
                    tmp_num = 1
                if translate_table.get(input[idx+1]) is None:
                    tmp_num *= 10
            elif current_word == 100:
                if translate_table.get(input[idx+1]) is None:
                    tmp_num *= 100
            else:
                tmp_num = tmp_num*10+current_word

        else:
            if tmp_num != 0:
                result_str += str(tmp_num)
                tmp_num = 0
            result_str += input[idx]
        idx += 1
    if tmp_num != 0:
        result_str += str(tmp_num)
    return result_str


def cut_sentences(content):
    end_flag = ['?', '!', '？', '！', '。', '…', '；','」']

    content = content.replace('\n', '')
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

# 已知問題：
# 1.目前尚無法讀取未加'民國'的2位數年分
# 2.有些非日期容易被讀取進來 Ex:3號出口、釋字第17號
# 3.若是句中重複出現'今'之類的關鍵字，會導致一段句子被重複讀取多次時間


def find_time(df: pd.DataFrame, tokenized=False):
    events_list = pd.DataFrame()
    if tokenized==False:
        timestamp = re.compile(
            '今[\(,（]\d+[日,號][\),）]|'
            '昨[\(,（]\d+[日,號][\),）]|'
            '[^至,迄]今[^年,\(,（]|'
            '昨[^\(（,]|'
            '[一,二,三,四,五,六,七,八,九,零,○]{4}年十?[一,二,三,四,五,六,七,八,九]?月?[二,三]?[一,二,三,四,五,六,七,八,九,十]?[一,二,三,四,五,六,七,八,九]?[日,號]?|'
            '十?[一,二,三,四,五,六,七,八,九]月[二,三]?[一,二,三,四,五,六,七,八,九,十]?[一,二,三,四,五,六,七,八,九]?[日,號]?|'
            '[二,三]?[一,二,三,四,五,六,七,八,九,十][一,二,三,四,五,六,七,八,九]?[日,號]'
            '民國\d{1,3}年\d{0,2}月?\d{0,2}[日,號]?|'
            '\d{3,4}年\d{0,2}月?\d{0,2}[日,號]?|'
            '\d{1,2}月\d{0,2}[日,號]?|'
            '(?<!\d)\d{1,2}[日,號]|'
            '今年\d{0,2}月?\d{0,2}[日,號]?|'
            '去年\d{0,2}月?\d{0,2}[日,號]?')
    else:
        timestamp = re.compile(
            '今 [\(,（] \d+[日,號] [\),）]|'
            '昨 [\(,（] \d+[日,號] [\),）]|'
            '[^至,迄]今[^年,\(,（][^\(,（]|'
            '昨[^\(,（][^\(,（]|'
            '[一,二,三,四,五,六,七,八,九,零,○]{4}年 ?十?[一,二,三,四,五,六,七,八,九]?月? ?[二,三]?[一,二,三,四,五,六,七,八,九,十]?[一,二,三,四,五,六,七,八,九]?[日,號]?|'
            '十?[一,二,三,四,五,六,七,八,九]月 ?[二,三]?[一,二,三,四,五,六,七,八,九,十]?[一,二,三,四,五,六,七,八,九]?[日,號]?|'
            '[二,三]?[一,二,三,四,五,六,七,八,九,十][一,二,三,四,五,六,七,八,九]?[日,號]'
            '民國 \d{1,3}年 ?\d{0,2}月? ?\d{0,2}[日,號]?|'
            '\d{3,4}年 ?\d{0,2}月? ?\d{0,2}[日,號]?|'
            '\d{1,2}月 ?\d{0,2}[日,號]?|'
            '(?<!\d)\d{1,2}[日,號]|'
            '今年 \d{0,2}月? ?\d{0,2}[日,號]?|'
            '去年 \d{0,2}月? ?\d{0,2}[日,號]?')
    
    for index, row in df.iterrows():
        try:
            publish_time = arrow.get(row['date'])
        except:
            publish_time = arrow.now()

        if tokenized==False:
            sentences = cut_sentences(str(row['paragraph']))
        else:
            sentences = cut_sentences(str(row['paragraph_tokens']))

        for sentence in sentences:
            time_list = timestamp.findall(sentence)
            if len(time_list) != 0:
                time = ''
                tmp_event = ''
                for idx, t in enumerate(time_list):
                    t = t.replace('(', '\(')
                    t = t.replace(')', '\)')
                    end = 0
                    if idx > 0:
                        try:
                            next = re.search(t, sentence).start(0)
                        except:
                            print(t)
                            continue
                        end = next
                        for i in range(next, -1, -1):
                            if sentence[i] == '，' or sentence[i] == '、':
                                end = i
                                break
                        event = tmp_event+sentence[:end]
                        events_list = pd.concat(
                            [events_list, pd.DataFrame({'Time': time, 'Event': event, 'Source': index+2}, index=[0])], ignore_index=True)
                    try:
                        next_start = re.search(t, sentence).end(0)
                    except:
                        print(t)
                        continue
                    tmp_event = sentence[end +
                                         1:next_start] if sentence[end] == '，' or sentence[end] == '、' else sentence[end:next_start]
                    sentence = sentence[next_start:]
                    t = t.replace('\(', '(')
                    t = t.replace('\)', ')')
                    time = chineses_to_num(t)
                    time = time.replace(' ','')
                    if re.match('(\d+)月(\d*)[日,號]?', time):
                        time = publish_time.format(
                            'YYYY/') + re.match('(\d+)月(\d*)[日,號]?', time).group(1)+ (
                                "" if not re.match('(\d+)月(\d*)[日,號]?', time).group(2) else "/" + re.match('(\d+)月(\d*)[日,號]?', time).group(2))
                    elif re.match('\d+[日,號]', time):
                        time = publish_time.format(
                            'YYYY/MM/') + re.match('(\d+)[日,號]', time).group(1)
                    elif re.match('今[\(,（]\d+[日,號][\),）]', time) or re.match('[^至,迄]?今[^年,\(,（]?', time):
                        time = publish_time.format('YYYY/MM/DD')
                    elif re.match('昨[\(,（]\d+[日,號][\),）]', time) or re.match('昨[^\(（,]?', time):
                        time = publish_time.shift(
                            days=-1).format('YYYY/MM/DD')
                    elif re.match('今年(\d*)月?(\d*)[日,號]?', time):
                        time = publish_time.format('YYYY') + (
                            '' if not re.match('今年(\d*)月?(\d*)[日,號]?', time).group(1) else "/" + re.match('今年(\d*)月?(\d*)[日,號]?', time).group(1)) + (
                            '' if not re.match('今年(\d*)月?(\d*)[日,號]?', time).group(2) else "/" + re.match('今年(\d*)月?(\d*)[日,號]?', time).group(2))
                    elif re.match('去年(\d*)月?(\d*)[日,號]?', time):
                        time = publish_time.shift(years=-1).format('YYYY') + (
                            '' if not re.match('去年(\d*)月?(\d*)[日,號]?', time).group(1) else "/" + re.match('去年(\d*)月?(\d*)[日,號]?', time).group(1)) + (
                            ''if not re.match('去年(\d*)月?(\d*)[日,號]?', time).group(2) else "/" + re.match('去年(\d*)月?(\d*)[日,號]?', time).group(2))
                    elif re.match('民國(\d+)年(\d*)月?(\d*)[日,號]?', time):
                        time = str(int(re.match('民國(\d+)年(\d*)月?(\d*)[日,號]?', time).group(1))+1911)+(
                            '' if not re.match('民國(\d+)年(\d*)月?(\d*)[日,號]?', time).group(2) else "/" + re.match('民國(\d+)年(\d*)月?(\d*)[日,號]?', time).group(2)) + (
                            '' if not re.match('民國(\d+)年(\d*)月?(\d*)[日,號]?', time).group(3) else "/" + re.match('民國(\d+)年(\d*)月?(\d*)[日,號]?', time).group(3))
                    elif re.match('(\d{3})年(\d{0,2}月?\d{0,2}[日,號]?)', time):
                        time = str(int(re.match('(\d{3})年(\d{0,2}月?\d{0,2}[日,號]?)', time).group(1))+1911)+(
                            "" if not re.match('(\d{3})年(\d{0,2})月?(\d{0,2})[日,號]?', time).group(2) else "/" + re.match('(\d{3})年(\d{0,2})月?(\d{0,2})[日,號]?', time).group(2))+(
                            "" if not re.match('(\d{3})年(\d{0,2})月?(\d{0,2})[日,號]?', time).group(3) else "/" + re.match('(\d{3})年(\d{0,2})月?(\d{0,2})[日,號]?', time).group(3))
                    time = time.replace('年','/')
                    time = time.replace('月','/')
                    time = time.replace('日','/')
                    if time[-1]=='/': time = time[:-1]
                    if re.match("(\d{4}/)(\d{1})(?!.)",time):
                        time=re.match("(\d{4}/)(\d{1})",time).group(1)+'0'+re.match("(\d{4}/)(\d{1})",time).group(2)

                    try:
                        fmt_time=arrow.get(time)
                        time=fmt_time.format("YYYY/MM/DD")
                    except:
                        print("Get time fail, time: "+ time)

                event = tmp_event+sentence
                events_list = pd.concat(
                    [events_list, pd.DataFrame({'Time': time, 'Event': event, 'Source': index+2}, index=[0])], ignore_index=True)

    return events_list


def str_to_time(s: str):
    time_patterns = [
        "YYYY年M月D日",
        "YYYY年",
        "YYYY年M月"
    ]
    arrow_time = None
    for pat in time_patterns:
        try:
            arrow_time = arrow.get(s, pat)
        except:
            continue
        break
    if arrow_time:
        return arrow_time.format("YYYY-MM-DD") + "T00:00:00Z"
    else:
        return ""

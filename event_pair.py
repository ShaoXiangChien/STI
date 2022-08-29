from datetime import tzinfo
from pprint import pprint
from unicodedata import numeric
import pandas as pd
from clean_df import *
import arrow

df = pd.read_csv('萊豬 output.csv', encoding='utf-8-sig')

result = clean_df(df)

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

def cut_sentences(content):
    end_flag = ['?', '!', '？', '！', '。', '…', '；']

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

timestamp=re.compile(
    '[一,二,三,四,五,六,七,八,九,零]{4}年十?[一,二,三,四,五,六,七,八,九]?月?[二,三]?十?[一,二,三,四,五,六,七,八,九]?[日,號]?|'
    '十?[一,二,三,四,五,六,七,八,九]月[二,三]?十?[一,二,三,四,五,六,七,八,九]?[日,號]?|'
    '[二,三]?[一,二,三,四,五,六,七,八,九,十][一,二,三,四,五,六,七,八,九]?[日,號]'
    '\d{4}年[一,二,三,四,五,六,七,八,九,十][一,二]?月?[二,三]?十?[一,二,三,四,五,六,七,八,九]?[日,號]?|'
    '\d{4}年\d{0,2}月?\d{0,2}[日,號]?|'
    '\d{1,2}月\d{0,2}[日,號]?|'
    '(?<!\d)\d{1,2}[日,號]|'
    '[^至,迄]今[^年]|'
    '昨|今年\d{0,2}月?\d{0,2}[日,號]?|'
    '去年\d{0,2}月?\d{0,2}[日,號]?')
timestamp_list = ['']
events_list = pd.DataFrame()
for index, row in df.iterrows():
    publish_time = arrow.now()
    try:
        publish_time = arrow.get(row['date'])
    except:
        pass
    sentences = cut_sentences(row['paragraph'])

    for sentence in sentences:

        time_list = re.findall(
            '\d{4}年\d{0,2}月?\d{0,2}[日,號]?|\d{1,2}月\d{0,2}[日,號]?|(?<!\d)\d{1,2}[日,號]|[^至,迄]今[^年]|昨|今年\d{0,2}月?\d{0,2}[日,號]?|去年\d{0,2}月?\d{0,2}[日,號]?', sentence)
        pos = 0
        if len(time_list) != 0:
            time = ''
            for idx, t in enumerate(time_list):
                if idx != 0:
                    next = re.search(t, sentence).start(0)
                    end = next-1
                    for i in range(next, pos-1, -1):
                        if sentence[i] == '，':
                            end = i
                            break
                    event = sentence[pos:end]
                    events_list = pd.concat(
                        [events_list, pd.DataFrame({'Time': time, 'Event': event}, index=[0])], ignore_index=True)
                    pos = end+1 if end == '，' else end+1
                time = t
                if re.match('\d+月\d*[日,號]?', time):
                    time = publish_time.format(
                        'YYYY年') + re.match('\d+月\d*[日,號]?', time).group()
                elif re.match('\d+[日,號]', time):
                    time = publish_time.format(
                        'YYYY年MM月') + re.match('\d+[日,號]', time).group()
                elif re.match('[^至,迄]今[^年]', time):
                    time = publish_time.format('YYYY年MM月DD日')
                elif re.match('昨', time):
                    time = publish_time.shift(days=-1).format('YYYY年MM月DD日')
                elif re.match('今年(\d*)月?(\d*)[日,號]?', time):
                    time = publish_time.format('YYYY年') + (
                        '' if not re.match('今年(\d*)月?(\d*)[日,號]?', time).group(1) else re.match('今年(\d*)月?(\d*)[日,號]?', time).group(1)+'月') + (
                        '' if not re.match('今年(\d*)月?(\d*)[日,號]?', time).group(2) else re.match('今年(\d*)月?(\d*)[日,號]?', time).group(2)+'日')
                elif re.match('去年(\d*)月?(\d*)[日,號]?', time):
                    time = publish_time.shift(years=-1).format('YYYY年') + (
                        '' if not re.match('去年(\d*)月?(\d*)[日,號]?', time).group(1) else re.match('去年(\d*)月?(\d*)[日,號]?', time).group(1)+'月') + (
                        ''if not re.match('去年(\d*)月?(\d*)[日,號]?', time).group(2) else re.match('去年(\d*)月?(\d*)[日,號]?', time).group(2)+'日')
            event = sentence[pos:]
            events_list = pd.concat(
                [events_list, pd.DataFrame({'Time': time, 'Event': event}, index=[0])], ignore_index=True)
        # # certain
        # if re.search('(\d*)年(\d*)月?(\d*)[日,號]?', sentence):
        #     time = re.search('(\d+)年(\d*)月?(\d*)[日,號]?', sentence).group()
        #     event = sentence
        #     events_list = pd.concat(
        #         [events_list, pd.DataFrame({'Time': time, 'Event': event}, index=[0])], ignore_index=True)
        # elif re.search('(\d+)月(\d*)[日,號]?', sentence):
        #     time = publish_time.format(
        #         'YYYY年') + re.search('(\d+)月(\d*)[日,號]?', sentence).group()
        #     event = sentence
        #     events_list = pd.concat(
        #         [events_list, pd.DataFrame({'Time': time, 'Event': event}, index=[0])], ignore_index=True)
        # elif re.search('(\d+)[日,號]', sentence):
        #     time = publish_time.format(
        #         'YYYY年MM月') + re.search('(\d+)[日,號]', sentence).group()
        #     event = sentence
        #     events_list = pd.concat(
        #         [events_list, pd.DataFrame({'Time': time, 'Event': event}, index=[0])], ignore_index=True)

        # if re.search('[^至,迄]今[^年]', sentence):
        #     time = publish_time.format('YYYY年MM月DD日')
        #     event = sentence
        #     events_list = pd.concat(
        #         [events_list, pd.DataFrame({'Time': time, 'Event': event}, index=[0])], ignore_index=True)
        # if re.search('昨', sentence):
        #     time = publish_time.shift(days=-1).format('YYYY年MM月DD日')
        #     event = sentence
        #     events_list = pd.concat(
        #         [events_list, pd.DataFrame({'Time': time, 'Event': event}, index=[0])], ignore_index=True)

        # if re.search('今年(\d*)月?(\d*)[日,號]?', sentence):
        #     time = publish_time.format('YYYY年') + (
        #         '' if not re.search('今年(\d*)月?(\d*)[日,號]?', sentence).group(1) else re.search('今年(\d*)月?(\d*)[日,號]?', sentence).group(1)+'月') + (
        #             ''if not re.search('今年(\d*)月?(\d*)[日,號]?', sentence).group(2) else re.search('今年(\d*)月?(\d*)[日,號]?', sentence).group(2)+'日')
        #     event = sentence
        #     events_list = pd.concat(
        #         [events_list, pd.DataFrame({'Time': time, 'Event': event}, index=[0])], ignore_index=True)
        # if re.search('去年(\d*)月?(\d*)[日,號]?', sentence):
        #     time = publish_time.shift(years=-1).format('YYYY年') + (
        #         '' if not re.search('去年(\d*)月?(\d*)[日,號]?', sentence).group(1) else re.search('去年(\d*)月?(\d*)[日,號]?', sentence).group(1)+'月') + (
        #             ''if not re.search('去年(\d*)月?(\d*)[日,號]?', sentence).group(2) else re.search('去年(\d*)月?(\d*)[日,號]?', sentence).group(2)+'日')
        #     event = sentence
        #     events_list = pd.concat(
        #         [events_list, pd.DataFrame({'Time': time, 'Event': event}, index=[0])], ignore_index=True)

events_list.to_csv('時間對應事件.csv', encoding='utf-8-sig', index=False)

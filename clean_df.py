from pprint import pprint
import pandas as pd
import re
import math


def clean_df(df):
    df.drop_duplicates(subset='title', inplace=True)
    df['title'] = df['title'].astype(str)
    df['paragraph'] = df['paragraph'].astype(str)

    for index, row in df.iterrows():
        row['paragraph'] = re.sub(row['title']+'\n', '', row['paragraph'])
        if row['source'] == 'udn.com':
            udn_expert_eyes = re.compile('【專家之眼】')
            udn_news_type = re.compile('.+／')
            udn_udn = re.compile('聯合新聞網')
            udn_listen_start = re.compile('0:00 / 0:00\n')
            udn_end1 = re.compile('延伸閱讀')
            udn_end2 = re.compile('（綜合報導）')
            udn_end3 = re.compile('贊助廣告')
            udn_news_info = re.compile('〔記者.+／.+報導〕')
            udn_keep_reading = re.compile('...繼續閱讀')

            row['title'] = re.sub(udn_udn, '', row['title'])
            row['title'] = re.sub(udn_expert_eyes, '', row['title'])
            row['title'] = re.sub(udn_news_type, '', row['title'])

            if udn_listen_start.search(row['paragraph']):
                start = udn_listen_start.search(row['paragraph']).span()[1]
                row['paragraph'] = row['paragraph'][start:]
            if udn_end1.search(row['paragraph']):
                stop = udn_end1.search(row['paragraph']).span()[0]
                row['paragraph'] = row['paragraph'][:stop]
            elif udn_end2.search(row['paragraph']):
                stop = udn_end2.search(row['paragraph']).span()[0]
                row['paragraph'] = row['paragraph'][:stop]
            elif udn_end3.search(row['paragraph']):
                stop = udn_end3.search(row['paragraph']).span()[0]
                row['paragraph'] = row['paragraph'][:stop]
            row['paragraph'] = re.sub(udn_news_info, '', row['paragraph'])
            row['paragraph'] = re.sub(udn_keep_reading, '', row['paragraph'])

        elif row['source'] == 'chinatimes.com':
            chinatimes_news_type = re.compile('.+》')
            chinatimes_end = re.compile('發表意見')

            row['title'] = re.sub(chinatimes_news_type, '', row['title'])
            if chinatimes_end.search(row['paragraph']):
                stop = chinatimes_end.search(row['paragraph']).span()[0]
                row['paragraph'] = row['paragraph'][:stop]

        elif row['source'] == 'setn.com':
            setn_news_info = re.compile('.+報導\n')
            setn_pict = re.compile('（圖／.+）')
            setn_vid = re.compile('（請看影片.+）')
            setn_url = re.compile('網址：.+')

            row['paragraph'] = re.sub(setn_news_info, '', row['paragraph'])
            row['paragraph'] = re.sub(setn_pict, '', row['paragraph'])
            row['paragraph'] = re.sub(setn_vid, '', row['paragraph'])
            row['paragraph'] = re.sub(setn_url, '', row['paragraph'])
            row['paragraph'] = row['paragraph'].replace('▲', '')
            row['paragraph'] = row['paragraph'].replace('▼', '')

        elif row['source'] == 'ltn.com':
            ltn_news_type = re.compile('.+》')
            ltn_news_info = re.compile('〔.+報導〕')
            ltn_break = re.compile('請繼續往下閱讀...\n')
            ltn_end1 = re.compile('☆健康新聞不漏接，按讚追蹤粉絲頁。')
            ltn_end2 = re.compile('不用抽 不用搶')

            row['title'] = re.sub(ltn_news_type, '', row['title'])
            row['paragraph'] = re.sub(ltn_news_info, '', row['paragraph'])
            row['paragraph'] = re.sub(ltn_break, '', row['paragraph'])
            if ltn_end1.search(row['paragraph']):
                stop = ltn_end1.search(row['paragraph']).span()[0]
                row['paragraph'] = row['paragraph'][:stop]
            elif ltn_end2.search(row['paragraph']):
                stop = ltn_end2.search(row['paragraph']).span()[0]
                row['paragraph'] = row['paragraph'][:stop]

        elif row['source'] == 'appledaily.com':
            apple_pict = re.compile('。.+攝\n')
            apple_news_info = re.compile('（.+報導）')
            apple_edit = re.compile('（新增：.+）\n')
            applle_update_time = re.compile('更新時間.+')  # 尚未使用

            row['paragraph'] = re.sub(apple_pict, '', row['paragraph'])
            row['paragraph'] = re.sub(apple_edit, '', row['paragraph'])
            if apple_news_info.search(row['paragraph']):
                stop = apple_news_info.search(row['paragraph']).span()[0]
                row['paragraph'] = row['paragraph'][:stop]

        elif row['source'] == 'news.yahoo.com':
            # Yahoo新聞為轉載各大新聞網站之新聞，因此種類眾多
            yahoo_news_type1 = re.compile('.+／')
            yahoo_news_type2 = re.compile('【.+】')
            yahoo_newtalk = re.compile('[新頭殼newtalk]\s*')
            yahoo_news_info1 = re.compile('.+ / .+報導\n')
            yahoo_news_info2 = re.compile('（.+／.+報導）\n')
            yahoo_news_info3 = re.compile('讀者投書：.+\n')
            yahoo_news_info4 = re.compile('文 ／.+\n')
            yahoo_news_info5 = re.compile('（編輯：.+）.+')
            yahoo_original_url = re.compile('.*原始網址：.+')
            yahoo_end1 = re.compile('【網路溫度計調查結果之圖文，未經授權請勿轉載、改寫】')
            yahoo_end2 = re.compile('《更多.*報導》')
            yahoo_end3 = re.compile('更多.*報導')
            yahoo_end4 = re.compile('＿{3,}')
            yahoo_end5 = re.compile('延伸閱讀》.+')
            yahoo_end6 = re.compile('更多相關新聞\n')
            yahoo_end7 = re.compile('更多.*文章')
            yahoo_end8 = re.compile('延伸閱讀：')
            yahoo_pict1 = re.compile('.*(.*圖/.+)\n|.*(.*圖／.+)\n')
            yahoo_pict2 = re.compile('照片來源：.+\n')

            row['title'] = re.sub(yahoo_news_type1, '', row['title'])
            row['title'] = re.sub(yahoo_news_type2, '', row['title'])

            if yahoo_end1.search(row['paragraph']):
                end = yahoo_end1.search(row['paragraph']).span()[0]
                row['paragraph'] = row['paragraph'][:end]
            elif yahoo_end2.search(row['paragraph']):
                end = yahoo_end2.search(row['paragraph']).span()[0]
                row['paragraph'] = row['paragraph'][:end]
            elif yahoo_end3.search(row['paragraph']):
                end = yahoo_end3.search(row['paragraph']).span()[0]
                row['paragraph'] = row['paragraph'][:end]
            elif yahoo_end4.search(row['paragraph']):
                end = yahoo_end4.search(row['paragraph']).span()[0]
                row['paragraph'] = row['paragraph'][:end]
            elif yahoo_end5.search(row['paragraph']):
                end = yahoo_end5.search(row['paragraph']).span()[0]
                row['paragraph'] = row['paragraph'][:end]
            elif yahoo_end6.search(row['paragraph']):
                end = yahoo_end6.search(row['paragraph']).span()[0]
                row['paragraph'] = row['paragraph'][:end]
            elif yahoo_end7.search(row['paragraph']):
                end = yahoo_end7.search(row['paragraph']).span()[0]
                row['paragraph'] = row['paragraph'][:end]
            if yahoo_end8.search(row['paragraph']):
                end = yahoo_end8.search(row['paragraph']).span()[0]
                row['paragraph'] = row['paragraph'][:end]

            row['paragraph'] = re.sub(yahoo_news_info1, '', row['paragraph'])
            row['paragraph'] = re.sub(yahoo_news_info2, '', row['paragraph'])
            row['paragraph'] = re.sub(yahoo_news_info3, '', row['paragraph'])
            row['paragraph'] = re.sub(yahoo_news_info4, '', row['paragraph'])
            row['paragraph'] = re.sub(yahoo_news_info5, '', row['paragraph'])
            row['paragraph'] = re.sub(yahoo_original_url, '', row['paragraph'])
            row['paragraph'] = re.sub(yahoo_newtalk, '', row['paragraph'])
            row['paragraph'] = re.sub(yahoo_pict1, '', row['paragraph'])
            row['paragraph'] = re.sub(yahoo_pict2, '', row['paragraph'])

        elif row['source'] == 'storm.mg':
            storm_news_type1 = re.compile('.+：')
            storm_news_type2 = re.compile('-新新聞')
            storm_news_type3 = re.compile('.+》')
            storm_timestamp = re.compile('\d\d\d\d-\d\d-\d\d \d\d:\d\d')
            storm_pict = re.compile('（.+照，.+攝）')

            row['title'] = re.sub(storm_news_type1, '', row['title'])
            row['title'] = re.sub(storm_news_type2, '', row['title'])
            row['title'] = re.sub(storm_news_type3, '', row['title'])
            if storm_timestamp.search(row['paragraph']):
                time = storm_timestamp.search(row['paragraph']).group()
                row['paragraph'] = re.sub(
                    storm_timestamp, '', row['paragraph'], 1)
                if math.isnan(row['date']):
                    row['date'] = time
            row['paragraph'] = re.sub(storm_pict, '', row['paragraph'])

        elif row['source'] == 'cna.com.tw':
            continue
    return df

from data_collection import *
from clean_df import *
# event = input("請輸入您想搜尋的事件:")
# n = int(input("欲爬取的google搜尋結果筆數:"))
event = '林智堅'
# n代表搜尋筆數而不是頁數
n = 100
# target_sources = ['setn.com']
target_sources = ['udn.com', 'chinatimes.com',
                  'news.tvbs.com', 'setn.com', 'ltn.com', 'appledaily.com', 'news.yahoo.com', 'storm.mg', 'cna.com.tw']

# output = news_to_df(target_sources, event, n)
# print(output)
result_df = google_search_api(event, n)
news, num = collect_target_news(target_sources, result_df)
if num != 0:
    news_df = pd.DataFrame()
    source_dt = {}
    for k, v in news.items():
        source_dt[k] = len(v)
        for piece in v:
            row = pd.DataFrame(parse_content(
                k, piece), index=[0])
            news_df = pd.concat([news_df, row], ignore_index=True)
news_df.to_csv(f"{event} output.csv", encoding="utf-8-sig", index=False)
cleaned_df = clean_df(news_df)
cleaned_df.to_csv(f'{event} cleaned.csv', encoding="utf-8-sig", index=False)

from data_collection_new import *

# event = input("請輸入您想搜尋的事件:")
# n = int(input("欲爬取的google搜尋結果筆數:"))
event = '萊豬'
# n代表搜尋筆數而不是頁數
n = 1000
target_sources = ['setn.com']
target_sources = ['udn.com', 'chinatimes.com',
                  'news.tvbs.com', 'setn.com', 'ltn.com', 'appledaily.com', 'news.yahoo.com', 'storm.mg', 'cna.com.tw']

# output = news_to_df(target_sources, event, n)
# print(output)
result_df = google_search_api(event, n)
print(f'num of result from serpapi : {len(result_df)}')
print(result_df)
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
print(news_df)
news_df.to_csv(f"{event} output.csv", encoding="utf-8-sig")

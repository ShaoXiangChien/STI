import pandas as pd
import requests
from pprint import pprint
import time
import google_search
import json


def parse_content(source, piece):
    response = google_search.get_source(piece['link'])
    title = ''
    date = ''
    article_contents = ''
    try:
        if source == 'udn.com':
            date = response.html.xpath("//div/section/time/text()")
            article_contents = response.html.xpath(
                "//section[@class='article-content__editor']/p/text()")
        elif source == 'chinatimes.com':
            pass
        elif source == 'news.tvbs.com':
            date = response.html.xpath("//div[@class='author']/br/text()")[0]
            article_contents = response.html.xpath(
                "//div[@class='article_content']/text()")
        elif source == 'setn.com':
            pass

        elif source == 'storm.mg':
            date = response.html.xpath(
                "//span[@class='info_inner_content']/text()")
            article_contents = response.html.xpath(
                "//div[@class='article_content_inner']/p/text()")
        elif source == 'ltn.com':
            date = response.html.xpath("//span[@class='time']/text()")
            article_contents = response.html.xpath(
                "//div[@class='text boxTitle boxText']/p[not(@*)]/text()")
            
        elif source == 'cna.com.tw':
            date = response.html.xpath("//div[@class='updatetime']/span/text()")
            article_contents = response.html.xpath("//div[@class='paragraph']/p/text()")

        elif source == 'news.yahoo.com':
            date = response.html.xpath(
                "//div[@class='caas-attr-time-style']/time/text()")[0]
            article_contents = response.html.xpath(
                "//div[@class='caas-body']/p/text()")


        elif source == 'appledaily.com':
            date = response.html.xpath(
                "//div[@class='timestamp']/text()[2]")[0]
            article_contents = response.html.xpath("//section/p/text()")
    except:
        pass

    return {'title': piece['title'], 'date': date, 'paragraph': ' '.join(article_contents), 'source': source}

    # return info


def collect_data(query, n):
    results = google_search.google_search(query, n)
    # with open('./result.json', 'w', encoding='utf8') as fh:
    #     json.dump(results, fh)
    target_sources = ['udn.com', 'chinatimes.com',
                      'news.tvbs.com', 'setn.com', 'ltn.com', 'appledaily.com', 'news.yahoo.com', 'storm.mg', 'cna.com.tw']
    desired_news = {ta: [] for ta in target_sources}
    for res in results:
        for ta in target_sources:
            if ta in res['link']:
                desired_news[ta].append(res)
                break
    return desired_news, len(results)


# if __name__ == '__main__':
#     print('data collection begins...')
#     tic = time.perf_counter()
#     news, num = collect_data('萊豬')
#     toc = time.perf_counter()
#     print(f"Collect the data in {toc - tic:0.4f} seconds")
#     print(f'# of results: {num}')
#     news_df = pd.DataFrame()
#     for k, v in news.items():
#         print(k, len(v))
#         for piece in v:
#             news_df = news_df.append(parse_content(
#                 k, piece), ignore_index=True)
#     # print(news_df)
#     news_df.to_csv('output.csv', index=False, encoding="utf-8-sig")

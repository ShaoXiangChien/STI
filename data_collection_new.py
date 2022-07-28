import requests
import pandas as pd
import arrow
import trafilatura
from lxml import etree
from requests_html import HTML
from requests_html import HTMLSession
from stqdm import stqdm
from datetime import tzinfo
from pprint import pprint
from serpapi import GoogleSearch
from api_secrets import serpapi_key


def google_search_api(query, n):
    search = GoogleSearch({
        "q": query,
        "location": "taipei",
        "api_key": serpapi_key,
        "num": n,
        "output": "json"
    })
    result = search.get_dict()
    output = []
    for res in result['organic_results']:
        item = {
            'title': res['title'],
            'link': res['link']
        }
        output.append(item)
    return output


def collect_target_news(target_sources, results):
    # with open('./result.json', 'w', encoding='utf8') as fh:
    #     json.dump(results, fh)
    desired_news = {ta: [] for ta in target_sources}
    for res in results:
        for ta in target_sources:
            if ta in res['link']:
                desired_news[ta].append(res)
                break
    return desired_news, len(results)


def get_source(url):
    """Return the source code for the provided URL.

    Args:
        url (string): URL of the page to scrape.

    Returns:
        response (object): HTTP response object from requests_html.
    """

    try:
        session = HTMLSession()
        response = session.get(url)
        return response

    except requests.exceptions.RequestException as e:
        print(e)


def parse_content(source, piece):
    link = piece['link']
    response = get_source(link)
    date_str = ''
    article_contents = ''
    content = trafilatura.fetch_url(link)
    article_contents = trafilatura.extract(content)

    if source == 'udn.com':
        # 'udn.com'會抓到經濟日報、轉角國際，但是其xpath與聯合報不同，需進行區分
        date_str = date_str.join(
            response.html.xpath("//div/section/time/text()"))
        # 聯合報時間格式：'YYYY-MM-DD HH:mm'
        try:
            date_str = arrow.get(
                date_str, 'YYYY-MM-DD HH:mm').replace(tzinfo='local')
        except:
            pass
        # article_contents = response.html.xpath(
        #     "//section[@class='article-content__editor']/p/text()")

    elif source == 'chinatimes.com':
        # 'chinatimes.com'會抓到Yahoo新聞的資料
        # 日期和時間在不同位置分開抓
        date = response.html.xpath(
            "//div[@class='meta-info-wrapper']/div[@class='meta-info']/time/span[@class='date']/text()")
        time_ = response.html.xpath(
            "//div[@class='meta-info-wrapper']/div[@class='meta-info']/time/span[@class='hour']/text()")
        date_str = ' '
        date_str = date_str.join(date + time_)
        # 中時時間格式：'YYYY/MM/DD HH:mm'
        try:
            date_str = arrow.get(
                date_str, 'YYYY/MM/DD HH:mm').replace(tzinfo='local')
        except:
            pass
        # article_contents = response.html.xpath(
        #     "//div[@class='article-body']/p/text()")

    elif source == 'news.tvbs.com':
        # 有時會選到新聞網搜尋系統的結果，導致Parse內容抓不到東西
        # TVBS時間格式：'\n\t\t\t\t\t\t\t發佈時間：YYYY/MM/DD HH:mm\t\t\t\t\t\t\t\n'
        date_str = date_str.join(response.html.xpath(
            "//div[@class='author']/text()[3]")).strip()
        date_str = date_str.replace('發佈時間：', '')
        try:
            date_str = arrow.get(
                date_str, 'YYYY/MM/DD HH:mm').replace(tzinfo='local')
        except:
            pass
        # article_contents = response.html.xpath(
        #     "//div[@class='article_content']/text()")

    elif source == 'setn.com':
        date_str = date_str.join(response.html.xpath(
            "//div[@class='page-title-text']/time[@class='page-date']/text()"))
        # 三立時間格式：'YYYY/MM/DD HH:mm:ss'
        try:
            date_str = arrow.get(
                date_str, 'YYYY/MM/DD HH:mm:ss').replace(tzinfo='local')
        except:
            pass
        # article_contents = response.html.xpath(
        #     "//*[@id='Content1']/p/text()")

    elif source == 'storm.mg':
        date_str = date_str.join(response.html.xpath(
            "//span[@class='info_inner_content']/text()"))
        # 風傳媒時間格式：'YYYY-MM-DD HH:mm'
        try:
            date_str = arrow.get(
                date_str, 'YYYY-MM-DD HH:mm').replace(tzinfo='local')
        except:
            pass
        # article_contents = response.html.xpath(
        #     "//div[@class='article_content_inner']/p/text()")

    elif source == 'ltn.com':
        date_str = date_str.join(response.html.xpath(
            "//span[@class='time']/text()")).strip()
        # 風傳媒時間格式：'YYYY/MM/DD HH:mm'
        try:
            date_str = arrow.get(
                date_str, 'YYYY/MM/DD HH:mm').replace(tzinfo='local')
        except:
            pass
        # article_contents = response.html.xpath(
        #     "//div[@class='text boxTitle boxText']/p[not(@*)]/text()")

    elif source == 'cna.com.tw':
        date_str = date_str.join(response.html.xpath(
            "//div[@class='updatetime']/span/text()"))
        print(f'CNA before : {date_str}')
        date_str = date_str[:16]
        print(f'after : {date_str}')
        # CNA時間格式：'YYYY/M/D HH:mm（M/D HH:mm 更新）'
        try:
            date_str = arrow.get(date_str).replace(tzinfo='local')
        except:
            pass
        # article_contents = response.html.xpath(
        #     "//div[@class='paragraph']/p/text()")

    elif source == 'news.yahoo.com':
        date_str = date_str.join(response.html.xpath(
            "//div[@class='caas-attr-time-style']/time/text()"))
        print(f'before : {date_str}')
        temp = ''
        i = 0
        while i < len(date_str):
            if date_str[i] == '週':
                i += 3
            elif date_str[i] == '下':
                temp += 'pm'
                i += 2
            elif date_str[i] == '上':
                temp += 'am'
                i += 2
            else:
                temp += date_str[i]
                i += 1
        date_str = temp
        print(f'after : {date_str}')
        try:
            date_str = arrow.get(
                date_str, 'YYYY年M月D日 Ah:mm').replace(tzinfo='local')
            print(f'sd : {date_str}')
        except:
            pass
        # article_contents = response.html.xpath(
        #     "//div[@class='caas-body']/p/text()")

    elif source == 'appledaily.com':
        date_str = date_str.join(response.html.xpath(
            "//div[@class='article__header']/div/div[@class='timestamp']/text()"))
        # article_contents = response.html.xpath(
        #     "//section/p[@class='text--desktop text--mobile article-text-size_md tw-max_width']")

    # print(type(date_str))
    # print(date_str)

    return {'title': piece['title'], 'date': date_str.format('YYYY/MM/DD HH:mm'), 'paragraph': ''.join(article_contents), 'source': source}


def news_to_df(target_sources, event, n):
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
    pprint(source_dt)
    return news_df

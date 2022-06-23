import requests
from bs4 import BeautifulSoup
from pprint import pprint


def crawl_wiki(kw):
    base_url = "https://zh.m.wikipedia.org/zh-tw/"
    url = base_url + kw
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    section = soup.find('section', attrs={'class': 'mf-section-0'})
    paragraphs = soup.find_all('p')

    for paragraph in paragraphs:
        for script in paragraph(['p']):
            script.decompose()

    strips = [list(paragraph.stripped_strings) for paragraph in paragraphs]
    paragraph = ''
    for words in strips:
        for word in words:
            if '[' not in word:
                paragraph += word
    return paragraph

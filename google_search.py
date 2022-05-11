import requests
import urllib
import pandas as pd
from lxml import etree
from requests_html import HTML
from requests_html import HTMLSession


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


def get_results(query):

    query = urllib.parse.quote_plus(query)
    response = get_source(
        "https://www.google.com/search?q=" + query + '&filter=0')
    responses = [response]
    for i in range(2, 100):
        url = response.html.xpath(f"//a[@aria-label='Page {i}']/@href")
        if len(url):
            new_res = get_source("https://www.google.com" + url[0])
            responses.append(new_res)
            if i == 10 or ((i - 10) % 4 == 0 and i > 10):
                response = new_res
        else:
            break

    return responses


def parse_results(response):

    css_identifier_result = ".tF2Cxc"
    css_identifier_title = "h3"
    css_identifier_link = ".yuRUbf a"
    css_identifier_text = ".VwiC3b"

    results = response.html.find(css_identifier_result)

    output = []

    for result in results:
        try:
            title = result.find(css_identifier_title, first=True).text
        except:
            title = ''
        try:
            link = result.find(css_identifier_link, first=True).attrs['href']
        except:
            link = ''
        try:
            text = result.find(css_identifier_text, first=True).text
        except:
            text = ''

        item = {
            'title': title,
            'link': link,
            'text': text
        }

        output.append(item)

    return output


def google_search(query):
    responses = get_results(query)
    results = []
    for response in responses:
        results += parse_results(response)
    return results

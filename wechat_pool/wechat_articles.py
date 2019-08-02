from urllib.parse import urlencode
import requests
from lxml.etree import XMLSyntaxError
from pyquery import PyQuery as pq
import pymongo
from wechat_pool.config import *


client = pymongo.MongoClient(MONGO_URI)
db = client[MONGO_DB]

base_url = 'https://weixin.sogou.com/weixin?'

headers = {
    'Cookies': 'SUV=00E3ECF0B724522D5D36E66235E24763; CXID=2355DD762D5B4EB363A09807565DE66D; ad=vZllllllll2NywwslllllVClkADlllllnhotxkllll9lllll4Oxlw@@@@@@@@@@@; SUID=061C2A3B3565860A5D40822F000E9366; IPLOC=CN4401; ABTEST=0|1564763202|v1; SNUID=790B17053D3BB119ECE58C923EFB16BA; weixinIndexVisited=1; sct=1; JSESSIONID=aaa3h-yikWVED8ibLwnXw',
    'Host': 'weixin.sogou.com',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
}


proxy = None


def get_proxy():
    try:
        response = requests.get(PROXY_URL_POOL)
        if response.status_code == 200:
            return response.text
        return None
    except ConnectionError:
        return None


def get_html(url, count=1):
    print('Cwarling', url)
    print('Try count', count)
    global proxy
    if count >= MAX_COUNT:
        print('tried too many count')
        return None

    try:
        if proxy:
            proxies = {
                'http': 'http://' + proxy
            }
            response = requests.get(url, allow_redirects=False, headers=headers, proxies=proxies)
        else:
            response = requests.get(url, allow_redirects=False, headers=headers)
        if response.status_code == 200:
            return response.text
        if response.status_code == 302:
            print('302')
            proxy = get_proxy()
            if proxy:
                print('Using proxy', proxy)
                return get_html(url)
            else:
                print('Get proxy failed')
                return None

    except ConnectionError as e:
        print('Error Occured', e.args)
        proxy = get_proxy()
        count += 1
        return get_html(url, count)


def get_index(keyword, page):
    data = {
        'query': keyword,
        'page': page,
        'type': 2
    }
    queries = urlencode(data)
    url = base_url + queries
    html = get_html(url)
    return html


def parse_index(html):
    doc = pq(html)
    items = doc('.news-box .news-list li .txt-box h3 a').items()
    for item in items:
        yield item.attr('href')


def get_detail(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None
    except ConnectionError:
        return None


def parse_detail(html):
    try:
        doc = pq(html)
        title = doc('.rich_media_title').text()
        content = doc('.rich_media_content').text()
        date = doc('#post-date').text()
        nickname = doc('.rich_media_list .rich_media_meta_nickname').text()
        wechat = doc('#js_profile_qrcode > div > p:nth-child(3) > span').text()

        return {
            'title': title,
            'content': content,
            'date': date,
            'nickname': nickname,
            'wechat': wechat
        }
    except XMLSyntaxError:
        return None


def save_to_mongo(data):
    if db['articles'].update({'title': data['title']}, {'$set': data}, True):
        print('saved to mongo', data['title'])
    else:
        print('saved to Mongo failed', data['title'])


def main():
    for page in range(1, 101):
        html = get_index(KEYWORD, page)
        if html:
            article_urls = parse_index(html)
            for article_url in article_urls:
                article_html = get_detail(article_url)
                if article_html:
                    article_data = parse_detail(article_html)
                    print(article_data)
                    if article_data:
                        save_to_mongo(article_data)


if __name__ == '__main__':
    main()


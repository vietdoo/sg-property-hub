import requests
import bs4 as BeautifulSoup
import time
import re
from datetime import datetime, date
import json
from .utils.config import *


def meeyland_list(url=None):
    max_num_page = 500
    crawl_url = "https://meeyland.com/mua-ban-nha-dat?page=1"
    if url:
        crawl_url = url

    # init variables with null or empty value
    products = []
    urls = []
    num_cur_page = int(crawl_url.split("=")[1])
    next_page = None

    # Case 0: getting 403 or 404... error. Try to get next page
    try:
        res = requests.get(crawl_url,
                           timeout=4)
    except:
        next_page = "https://meeyland.com/mua-ban-nha-dat?page=" + \
            str(num_cur_page + 1)
        return {'urls': urls, 'next_page': next_page}

    soup = BeautifulSoup.BeautifulSoup(res.text, 'html.parser')
    products = soup.find_all(
        'div', class_='slider-hover')

    # Case 1: products is not empty and current page is bigger than max_num_page
    if not products and num_cur_page > max_num_page:
        raise Exception('Crawling Finished')

    # Case 2: 200 status code and products is not empty or current page is smaller than max_num_page
    for product in products:
        try:
            urls.append('https://meeyland.com' + product.find('a')['href'])
        except:
            pass

    next_page = "https://meeyland.com/mua-ban-nha-dat?page=" + \
        str(num_cur_page + 1)
    return {'urls': urls, 'next_page': next_page}


def meeyland_item(url):

    item = {}
    res = requests.get(url,
                       proxies = PROXY)
    soup = BeautifulSoup.BeautifulSoup(res.text, 'html.parser')

    # find <script id="__NEXT_DATA__" type="application/json">
    try:
        script = soup.find('script', {'id': '__NEXT_DATA__'})
        data = json.loads(script.text)
    except:
        raise Exception('Cannot extract data from script (meeyland) with url: ' + res.text)

    try:
        data = data['props']['pageProps']['article']
    except:
        raise Exception('Cannot extract data from script (meeyland) with url: ' + url)

    item = {}
    item['title'] = data['title']
    item['url'] = url
    item['site'] = 'meeyland'

    item['price'] = data['price']['total']
    item['price_currency'] = 'VND'
    item['price_string'] = data['priceLabel']

    try:
        item['images'] = [img['url'] for img in data['images']]
    except:
        pass

    item['description'] = data['content']
    item['property_type'] = data['typeOfHouse'][0]
    item['publish_at'] = datetime.strptime(
        data['publishedDate'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime("%Y-%m-%d %H:%M:%S")

    item['attr'] = {}

    item['attr']['area'] = data['area']
    item['attr']['total_area'] = data['areaUse']
    item['attr']['width'] = data['facade']
    item['attr']['length'] = data['depth']
    item['attr']['bathroom'] = data['bathroom']
    item['attr']['floor'] = data['floor']

    item['attr']['direction'] = (', ').join(data['direction']) if data['direction'] else None
    data['furniture'] = [] if 'furniture' not in data else data['furniture']
    data['equipment'] = [] if 'equipment' not in data else data['equipment']
    data['utilities'] = [] if 'utilities' not in data else data['utilities']
    data['feature'] = [] if 'feature' not in data else data['feature']
    data['legalPaper'] = [] if 'legalPaper' not in data else data['legalPaper']

    item['attr']['interior'] = (', ').join(
        [furniture['label'] for furniture in data['furniture'] or []])
    for equipment in data['equipment'] or []:
        item['attr']['interior'] += ', ' + equipment['label']

    item['attr']['feature'] = (', ').join(
        [utilities['label'] for utilities in data['utilities'] or []])

    for feature in data['feature'] or []:
        for option in feature['options'] or []:
            item['attr']['feature'] += ', ' + option['label']

    item['attr']['certificate'] = (', ').join(
        [legalPaper for legalPaper in data['legalPaper'] or []])

    item['attr']['type_detail'] = data['typeOfRealEstate']
    item['attr']['siteid'] = str(data['code'])

    item['location'] = {}
    item['location']['city'] = data['location']['city']
    item['location']['dist'] = data['location']['district']
    try:
        item['location']['ward'] = data['location']['ward']
    except:
        pass
    try:
        item['location']['street'] = data['location']['street']
    except:
        pass
    try:
        item['location']['address'] = data['address']
    except:
        pass

    try:
        item['location']['long'] = data['geoloc'][0]
        item['location']['lat'] = data['geoloc'][1]
    except:
        pass
    item['location']['description'] = data['wideRoad']

    item['agent'] = {}
    item['agent']['name'] = data['contact']['name']
    item['agent']['phone_number'] = data['contact']['phone']
    item['agent']['email'] = data['contact']['email']

    item['projecct'] = {}
    try:
        item['projecct']['name'] = data['location']['project']
    except:
        pass
    return item

import requests
import bs4 as BeautifulSoup
import time
import re
from datetime import datetime, date
import json
from .utils.config import *

def mogi_list(url = None):
    max_num_page = 39200
    crawl_url = "https://mogi.vn/mua-nha-dat?cp=1"
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
                           timeout = 4)
    except:
        next_page = "https://mogi.vn/mua-nha-dat?cp=" + \
            str(num_cur_page + 1)
        return {'urls': urls, 'next_page': next_page}

    soup = BeautifulSoup.BeautifulSoup(res.text, 'html.parser')
    products = soup.find('div', class_='property-listing').find('ul', class_='props').find_all('a')
    
    # Case 1: products is not empty and current page is bigger than max_num_page
    if not products and num_cur_page > max_num_page:
        raise Exception('Crawling Finished')

    # Case 2: 200 status code and products is not empty or current page is smaller than max_num_page
    for product in products:
        try:
            urls.append(product['href'])
        except:
            pass
        
    next_page = "https://mogi.vn/mua-nha-dat?cp=" + \
        str(num_cur_page + 1)
    return {'urls': urls, 'next_page': next_page}



def mogi_item(url):

    item = {}
    res = requests.get(url,
                       proxies = PROXY)
    soup = BeautifulSoup.BeautifulSoup(res.text, 'html.parser')

    item = {}
    main_info = soup.find('div', class_='main-info')
    script = soup.find('script', type='application/ld+json')
    script_data = json.loads(script.text)
    
    title = main_info.find('div', class_='title').text.strip('\n').strip()
    item['title'] = title

    item['site'] = 'mogi'
    item['url'] = url
    
    item['price'] = script_data['makesOffer']['priceSpecification']['price']
    item['price_currency'] = script_data['makesOffer']['priceSpecification']['priceCurrency']

    description = script_data['makesOffer']['itemOffered']['description']
    item['description'] = description

    item['property_type'] = script_data['makesOffer']['itemOffered']['@type']

    images = []
    slides = soup.find_all('div', class_='media-item')
    for slide in slides:
        try:
            images.append(slide.find('img')['data-src'])
        except:
            pass

        try:
            images.append(slide.find('img')['src'])
        except:
            pass
    item['images'] = images

    item['attr'] = {}

    attrs = soup.find('div', class_='info-attrs').text.split('\n')
    attrs = [attr for attr in attrs if attr]

    for i in range(0, len(attrs), 2):
        try:
            key = attrs[i]
            value = attrs[i+1]
            if key == 'Diện tích sử dụng':
                value = int(value.split(' ')[0].strip())
                item['attr']['total_area'] = value

            if key == 'Diện tích đất':
                value = int(value.split(' ')[0].strip())
                item['attr']['area'] = value

                wh = re.findall(r'\((.*?)\)', attrs[i+1])[0]
                item['attr']['width'] = float(wh.split('x')[0].strip().replace(',', '.'))
                item['attr']['length'] = float(wh.split('x')[1].strip().replace(',', '.'))

            if key == 'Phòng ngủ':
                value = int(value.split(' ')[0].strip())
                item['attr']['bedroom'] = value

            if key == 'Nhà tắm':
                value = int(value.split(' ')[0].strip())
                item['attr']['bathroom'] = value

            if key == 'Pháp lý':
                value = value.strip()
                item['attr']['certificate'] = value
            
            if key == 'Mã BĐS':
                value = value.strip()
                item['attr']['site_id'] = value
            
            if key == 'Ngày đăng':
                value = value.split(' ')[0].strip()
                value = datetime.strptime(value, '%d/%m/%Y').strftime("%Y-%m-%d %H:%M:%S")
                item['publish_at'] = value


        except Exception as e:
            print('Error when parse attr', e)
            pass


    item['location'] = {}
    try:
        item['location']['address'] = description = script_data['makesOffer']['itemOffered']['address']
    except:
        pass
    
    breadcumb = soup.find('ul', attrs={'class': 'breadcrumb', 'typeof': 'BreadcrumbList'})

    item['location']['city'] = breadcumb.find_all('li')[2].text
    item['location']['dist'] = breadcumb.find_all('li')[3].text

    item['location']['description'] = breadcumb.find_all('li')[4].text
    
    try:
        map_data = soup.find('iframe', attrs={'title': 'map'})['data-src'].split('q=')[1]
        item['location']['lat'] = float(map_data.split(',')[0])
        item['location']['long'] = float(map_data.split(',')[1])
    except:
        pass

    item['agent'] = {}
    try:
        item['agent']['name'] = script_data['name']
    except:
        pass

    try:
        item['agent']['agent_type'] = script_data['@type']
    except:
        pass

    try:
        item['agent']['phone_number'] = script_data['telephone']
    except:
        pass
    return item
import requests
import re
from datetime import datetime
import logging
import json
# from property_crawler.items import PropertyCrawlerItem
from decimal import Decimal
from bs4 import BeautifulSoup
import time
from .utils.config import *

def batdongssan_so_list(url = None):
    max_num_page = 15000
    crawl_url = 'https://batdongsan.so/api/v1/home/demand/1/posts?page=1'
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
                           proxies = PROXY)
    except:
        next_page = "https://batdongsan.so/api/v1/home/demand/1/posts?page=" + \
            str(num_cur_page + 1)
        return {'urls': urls, 'next_page': next_page}

    products = res.json()
    products = products["data"]

    # Case 1: products is not empty and current page is bigger than max_num_page
    if not products and num_cur_page > max_num_page: 
        raise Exception('Crawling Finished')
     
    # Case 2: 200 status code and products is not empty or current page is smaller than max_num_page
    for product in products:
        try:
            url = product["url"]
            urls.append(url)
        except:
            pass
    next_page = "https://batdongsan.so/api/v1/home/demand/1/posts?page=" + \
        str(num_cur_page + 1)

    return {'urls': urls, 'next_page': next_page}

def convert_price(price):
    list_price = price.split(" ")
    sum_price = 0
    for i in range(len(list_price)):
        if list_price[i] == "tỷ":
            sum_price+= float(list_price[i-1].replace(",",".")) * (10**9)
        elif list_price[i] == "triệu":
            sum_price+= float(list_price[i-1].replace(",",".")) * (10**6)
    return int(sum_price)

def convert_main_info(main_info_string):
    list_info_string = main_info_string.split("\n")
    main_info={}
    for info in list_info_string:
        if info.find(":") != -1:
            key,value = info.split(":")
            main_info[key.strip()] = value.strip()
    return main_info

def batdongssan_so_item(url):
    res = requests.get(url,
                       proxies = PROXY)

    soup = BeautifulSoup(res.text, 'html.parser')
    item = {}

    title= soup.find("h1",class_="re-title").getText().strip()
    item["title"]=title
    
    item["site"]='batdongsan_so'
    item["url"] = res.url
    
    price_string = soup.find("div",class_="re-price").getText().split(":")[1].strip()
    if price_string == 'Liên hệ':
        item["price_string"] = price_string 
    else:
        price = convert_price(price_string)
        item["price"] = price
        item["price_string"] = price_string
    
    images_list=[]
    images = soup.find("div",class_="re-gallery").find_all("img")
    for i in range(int(len(images)/2)):
        image = images[i]["src"]
        images_list.append(image)
    item["images"]= images_list
    
    item["description"]=soup.find("div",class_="re-content").get_text().strip()
    
    detail = soup.findAll("span",class_="sp3")
    date = detail[0].get_text()
    item["publish_at"] = datetime.strptime(date, '%d/%m/%Y').strftime("%Y-%m-%d %H:%M:%S")
    
    item["location"] = {}
    cate_loc = soup.find("div",class_="re-district").find_all("a")
    item["property_type"]=cate_loc[0].get_text().replace("Bán","").strip()
    
    item["location"]["city"] = cate_loc[1].get_text()
    
    item["location"]["dist"]= cate_loc[2].get_text()
    
    item["location"]["adress"]= soup.find("div",class_="re-address").get_text().strip()
    
    item["attr"] = {}
    main_info_string = soup.find("ul",class_="re-property").get_text().strip()
    main_info=convert_main_info(main_info_string)
    try:
        if 'Diện tích' in main_info:
            area = float(main_info['Diện tích'].replace("m2","").replace(",","."))
            item["attr"]["area"] = area
            item["attr"]["total_area"] = area
            
        if 'Hướng' in main_info:
            item["attr"]["direction"] = main_info["Hướng"]
        
        if 'Mặt tiền' in main_info:
            item["attr"]["width"] = float(main_info["Mặt tiền"])
            
        if 'Số toilet' in main_info:
            item["attr"]["bathroom"] = int(main_info['Số toilet'])
            
        if 'Số phòng ngủ' in main_info:
            item["attr"]["bedroom"] = int(main_info['Số phòng ngủ'])
        
        if 'Số tầng' in main_info:
            if item["property_type"] == 'căn hộ - chung cư':
                item["attr"]["floor_num"] = int(main_info["Số tầng"])
            else:
                item["attr"]["floor"] = int(main_info["Số tầng"])
    except Exception as e:
        print('Error when parse attr', e)
        pass
    
    item["agent"]={}
    info = soup.find("div",class_ ="info").find("a")
    try:

        item["agent"]["name"] = info.get_text().strip()
    except:
        pass
    
    try:
        item["agent"]["profile"] = info["href"]
    except:
        pass
    
    
    return item
    
    
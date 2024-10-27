import requests
import re
from datetime import datetime,date,timedelta
import logging
import json
# from property_crawler.items import PropertyCrawlerItem
from decimal import Decimal
from bs4 import BeautifulSoup
import time
from .utils.config import *

def ibatdongsan_list(url = None):
    max_num_page = 11015
    crawl_url = 'https://i-batdongsan.com/can-ban-nha-dat.htm'
    if url:
        crawl_url = url
    # init variables with null or empty value
    products = []
    urls = []
    try:
        num_cur_page = int(crawl_url.split("/p")[1].split(".")[0])
    except:
        num_cur_page = 1
    next_page = None  
    
    # Case 0: getting 403 or 404... error. Try to get next page
    try:   
        res = requests.get(crawl_url,
                           timeout=4)
    except:
        next_page = "https://i-batdongsan.com/can-ban-nha-dat/p" + str(num_cur_page + 1)+".htm"
        return {'urls': urls, 'next_page': next_page}
    
    
    soup = BeautifulSoup(res.text, 'html.parser')
    products = soup.find_all("div",class_="thumbnail")
    
     # Case 1: products is not empty and current page is bigger than max_num_page
    if not products and num_cur_page > max_num_page:
        raise Exception('Crawling Finished')
    elif products:
    #2: 200 status code and products is not empty or current page is smaller than max_num_page    
        for product in products:
            try:
                url = "https://i-batdongsan.com"+ product.find("a")["href"]
                urls.append(url)
            except:
                pass
    next_page = "https://i-batdongsan.com/can-ban-nha-dat/p" + str(num_cur_page + 1)+".htm"
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

def convert_main_info(main_info_document):
    main_info ={}
    feature = ''
    for i in main_info_document:
        temp = i.find_all("td")

        if temp[1].get_text() != "---":
            main_info[temp[0].get_text()] = temp[1].get_text()
        if len(temp) >= 4:
            if (temp[3].get_text() != "---") and (temp[3].get_text() != "_") :
                main_info[temp[2].get_text()] = temp[3].get_text()
        if len(temp) == 6:
            if len(temp[5].get_text()) ==0:
                feature+= temp[4].get_text()+","
    if len(feature) > 0 :
        main_info["feature"] = feature[:-1]
    return main_info

def convert_address_info(address):
     #full string_format : "10 ngõ 55, Đường Lê Quý Đôn, Phường Bạch Đằng, Quận Hai Bà Trưng, Hà Nội"
     # convert to address,city,dist,ward,street
    info = {}
    info["address"] = address
    list_info = address.split(", ")
    list_loc = ["city","dist","ward","street"]
    for i in range(len(list_loc)):
        if len(list_info) - i -1 >= 0 :
            info[list_loc[i]] = list_info[len(list_info) - i -1]
    return info

def ibatdongsan_item(url):
    
    res = requests.get(url,
                       proxies = PROXY)    
    soup = BeautifulSoup(res.text, 'html.parser')
    item = {}
    
    title = soup.find("div",class_="title").get_text()
    item["title"]=title
    
    item["site"] = 'i-batdongsan'
    item["url"] = res.url
    
    main_info_doc = soup.find("div",class_='infor').find("table")
    main_info = convert_main_info(main_info_doc)
    
    price = convert_price(main_info["Giá"])
    item["price"] = price
    item["price_string"] = main_info["Giá"]
    
    images_list = []
    try:
        images = soup.find("div",class_="image-list").find_all("img")
        for image in images:
            img_url = 'https://i-batdongsan.com'+ image['src']
            images_list.append(img_url)
    except:
        pass
    item["images"] = images_list
    
    item["description"] = soup.find("div",class_="detail text-content").get_text()
    
    item["property_type"]= main_info["Loại BDS"]
    
    if main_info["Ngày đăng"] == 'Hôm nay':
        timevalue = date.today().strftime("%Y-%m-%d %H:%M:%S")
    elif main_info["Ngày đăng"] == 'Hôm qua':
        timevalue = (date.today() - timedelta(1)).strftime("%Y-%m-%d %H:%M:%S")
    else:
        timevalue = datetime.strptime(main_info["Ngày đăng"], '%d/%m/%Y').strftime("%Y-%m-%d %H:%M:%S")
    item["publish_at"] = timevalue
    
    #{'Ngày đăng': 'Hôm nay', 'Mã tin': '4722431', 'Loại tin': 'Cần bán', 'Lộ giới': '16m', 'Loại BDS': 'Biệt thự', 'Pháp lý': 'Sổ hồng/ Sổ đỏ', 'Chiều ngang': '8m', 'Số lầu': '3', 'Chiều dài': '54m', 'Số phòng ngủ': '9', 'Diện tích': '430m2', 'Giá': '55 tỷ ', 'feature': 'Phòng ăn,Nhà bếp,Sân thượng,Chổ để xe hơi'}
    address = soup.find("div",class_="address").get_text().split(":")[1]
    item["location"] = convert_address_info(address)
    
    item["attr"] = {}
    try:
        if 'Diện tích' in main_info:
            area = float(main_info["Diện tích"].replace("m2","").replace(",","."))
            item["attr"]["area"] = area
            item["attr"]["total_area"] = area
            
        if 'Chiều ngang' in main_info:
            item["attr"]['width'] = float(main_info["Chiều ngang"].replace("m","").replace(",","."))
            
        if 'Chiều dài' in main_info:
            item["attr"]["length"] = float(main_info["Chiều dài"].replace("m","").replace(",","."))
        
        if 'Số phòng ngủ' in main_info:
            item["attr"]["bedroom"]= int(main_info["Số phòng ngủ"])
            
        if 'Số lầu' in main_info:
            if item["property_type"] == "Căn hộ chung cư":
                item["attr"]["floor_num"] = int(main_info["Số lầu"])
            else:
                item["attr"]["floor"] = int(main_info["Số lầu"])
        
        if 'Hướng' in main_info:
            item["attr"]["direction"] = main_info["Hướng"]
        
        if 'feature' in main_info:
            item["attr"]["feature"] = main_info["feature"]
        
        if 'Pháp lý' in main_info:
            item["attr"]["certificate"]= main_info["Pháp lý"]
        
        if 'Mã tin' in main_info:
            item["attr"]["site_id"] = main_info["Mã tin"]
    
    except Exception as e:
            print('Error when parse attr', e)
            pass
    
    item["agent"] = {}
    try:
        item["agent"]["name"] = soup.find("div",class_="name").get_text()
    except:
        pass
    
    try:
        item["agent"]["phone_number"]=soup.find("div",class_="fone").get_text().replace(".","")
    except:
        pass
    
    return item
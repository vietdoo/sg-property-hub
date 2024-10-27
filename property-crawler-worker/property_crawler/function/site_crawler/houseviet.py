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

def houseviet_list(url = None):
    max_num_page = 8030
    crawl_url = 'https://houseviet.vn/nha-dat-ban'
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
        next_page = "https://houseviet.vn/nha-dat-ban/p" + str(num_cur_page + 1)
        return {'urls': urls, 'next_page': next_page}

    soup = BeautifulSoup(res.text, 'html.parser')
    products =soup.find_all("section",class_="property-item")
    
    # Case 1: products is not empty and current page is bigger than max_num_page
    if not products and num_cur_page > max_num_page:
        raise Exception('Crawling Finished')
    elif products:
    #2: 200 status code and products is not empty or current page is smaller than max_num_page
        for product in products:
            try: 
                urls.append(product.find("a")["href"])
            except:
                pass
    next_page = "https://houseviet.vn/nha-dat-ban/p" + str(num_cur_page + 1)
    return {'urls': urls, 'next_page': next_page}

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

def convert_price(price):
    list_price = price.split(" ")
    sum_price = 0
    for i in range(len(list_price)):
        if list_price[i] == "tỉ":
            sum_price+= float(list_price[i-1].replace(",",".")) * (10**9)
        elif list_price[i] == "triệu":
            sum_price+= float(list_price[i-1].replace(",",".")) * (10**6)
    return int(sum_price)   

def convert_main_info(soup):
    info = {}
    try:
        a =soup.find("div",class_="property-spec-body").find_all("li")
        for i in a:
            temp= i.find_all("span")
            if temp[1].get_text().strip() != '---':
                info[temp[0].get_text()] = temp[1].get_text().strip()
    except:
        pass
    try: 
        a =soup.find_all("div",class_="property-spec-other")[0].find_all("li")
        for i in a:
            temp= i.find_all("span")
            if temp[1].get_text().strip() != '---':
                info[temp[0].get_text()] = temp[1].get_text().strip()
    except:
        pass
    try:
        a =soup.find_all("div",class_="property-spec-other")[1].find_all("li")
        for i in a:
            temp= i.find_all("span")
            if temp[1].get_text().strip() != '---':
                info[temp[0].get_text()] = temp[1].get_text().strip()
    except:
        pass
    try:  
        a =soup.find("div",class_="d-flex justify-content-between mt-3 pb-2 border-bottom").find_all("span")
        if a[1].get_text().strip() != '---':
                info[a[0].get_text()] = a[1].get_text()
    except:
        pass
    return info

def houseviet_item(url):

    res = requests.get(url,
                       proxies = PROXY)    
    soup = BeautifulSoup(res.text, 'html.parser')
    item = {}
    
    title=soup.find("h1",class_="text-uppercase fs-6").get_text()
    item["title"] = title
    
    item["site"] = 'houseviet'
    item["url"] = res.url
    
    price_string = soup.find("div",class_="text-red").get_text()
    if price_string == 'Giá thỏa thuận':
        item["price_string"] = price_string
    else:
        price_list= price_string.split("~ ")
        if  price_list[0].find("/") == -1:
            price= convert_price(price_list[0])
            item["price"]=price
            item["price_string"]=price_list[0]
        else:
            price= convert_price(price_list[1])
            item["price"]=price
            item["price_string"]=price_list[1]
    
    
    images_list =[]
    item["images"] = images_list
    
    description = soup.find("div",class_="property-description").get_text()
    item["description"] =description[16:]
    
    detail = soup.find_all("div",class_="text-muted")
    try:
        item["publish_at"] = detail[2].find("span")["data-time"].split(".")[0].replace("T"," ")
    except:
        pass
    
    item["property_type"] =detail[1].find("span").get_text().replace("Bán ","").strip()
    
    main_info = convert_main_info(soup)
    item["location"]={}
    try:
        address = main_info["Địa chỉ:"]
        item["location"] = convert_address_info(address)
    except Exception as e:
        print('Error when parse location', e)
        pass
    
    item["attr"] ={}
    area = soup.find_all("div",class_="highlight-value")[1].get_text()
    if area != '---' :
        item["attr"]["area"]= float(area.split(" ")[0].replace(".","").replace(",","."))
    item["attr"]["site_id"] = detail[0].find("span").get_text()
    try:
        if 'Diện tích sử dụng:' in main_info:
            item["attr"]["area"] = float(main_info["Diện tích sử dụng:"].split(" ")[0].replace(".","").replace(",","."))
            
        if 'Mặt tiền: ' in main_info:
            item["attr"]["width"]= int(main_info["Mặt tiền: "].split(" ")[0])
            
        if 'Chiều sâu: ' in main_info:  
            item["attr"]["width"]= int(main_info["Chiều sâu: "].split(" ")[0])
            
        if 'Giấy tờ pháp lý:' in main_info:
            item["attr"]["certificate"] = main_info["Giấy tờ pháp lý:"]
            
        if 'Số phòng ngủ: ' in main_info:
            item["attr"]["bedroom"] = int(main_info["Số phòng ngủ: "].split(" ")[0])
            
        if 'Số phòng vệ sinh: ' in main_info:
            item["attr"]["bathroom"] = int(main_info["Số phòng vệ sinh: "].split(" ")[0])
            
        if 'Tổng số tầng: ' in main_info:
            item["attr"]["floor"] = int(main_info["Tổng số tầng: "].split(" ")[0])
            
        if 'Vị trí tầng bán: ' in main_info:
            item["attr"]["floor_num"] = int(main_info["Vị trí tầng bán: "].split(" ")[2])
            
        if 'Nội thất: ' in main_info:
            item["attr"]["interior"] = main_info["Nội thất: "]
            
        if 'Hướng nhà/đất: ' in main_info:
            item["attr"]["direction"]=main_info["Hướng nhà/đất: "]
            
    except Exception as e:
            print('Error when parse attr', e)
            pass
        
    item["agent"]={}
    agent_info = soup.find("div",class_="info").find_all("div")
    try:
        item["agent"]["name"] = agent_info[0].get_text()
    except:
        pass
    
    try:
        item["agent"]["agent_type"] = agent_info[1].get_text()
    except:
        pass
    
    try:
        item["agent"]["phone_number"] = soup.find("div",class_="seller-contact mt-2").get_text().strip()
    except:
        pass
    return item
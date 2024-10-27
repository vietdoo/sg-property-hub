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

def nhadat24h_list(url = None):
    max_num_page = 6129
    crawl_url ="https://nhadat24h.net/nha-dat-ban/page1"
    if url:
        crawl_url = url
        
    # init variables with null or empty value
    products = []
    urls = []
    num_cur_page = int(crawl_url.split("/page")[1])
    next_page = None  

    # Case 0: getting 403 or 404... error. Try to get next page
    try:   
        res = requests.get(crawl_url,
                           timeout=4)
    except:
        next_page = "https://nhadat24h.net/nha-dat-ban/page" + str(num_cur_page + 1)
        return {'urls': urls, 'next_page': next_page}
    
    soup = BeautifulSoup(res.text, 'html.parser')
    list_product = soup.find("div",id="ContentPlaceHolder2_KetQuaTimKiem1_Pn1")

    # Case 1: products is not empty and current page is bigger than max_num_page
    if not list_product and num_cur_page > max_num_page:
        raise Exception('Crawling Finished')
    elif list_product: 
        products = list_product.find_all("a",class_="a-title")
        for product in products:
            try:
                url = "https://nhadat24h.net"+ product["href"]
                urls.append(url)
            except:
                pass
    next_page = "https://nhadat24h.net/nha-dat-ban/page" + str(num_cur_page + 1)
    return {'urls': urls, 'next_page': next_page}

      
def convert_price(price):
    sum_price = 0
    if price.find("Tỷ") != -1:
        sum_price+= float(price.replace("Tỷ ","").replace(",",".")) * (10**9)
    elif price.find("Triệu") != -1:
        sum_price+= float(price.replace("Triệu ","").replace(",",".")) * (10**6)
    return int(sum_price)
    
def convert_address_info(address):
     #full string_format : "10 ngõ 55, Đường Lê Quý Đôn, Phường Bạch Đằng, Quận Hai Bà Trưng, Hà Nội"
     # convert to address,city,dist,ward,street
    info = {}
    info["address"] = address
    list_info = address.split(", ")
    list_loc = ["city","dist","ward"]
    for i in range(len(list_loc)):
        if len(list_info) - i -1 >= 0 :
            info[list_loc[i]] = list_info[len(list_info) - i -1]
    return info

def nhadat24h_item(url):

    res = requests.get(url,
                       proxies = PROXY)    
    soup = BeautifulSoup(res.text, 'html.parser')
    item = {}
    
    title = soup.find("h1",id="txtcontenttieudetin").get_text()
    item["title"] = title
    
    item["site"] = 'nhadat24h'
    item["url"] = res.url
    
    detail = soup.find("div", class_="dv-time-dt").find_all("p")
    price_area = detail[0].get_text().split(":")[1]
    price_string,area_string = price_area.split("-")
    
    if price_string == 'Thỏa thuận':
        item["price_string"] = price_string 
    else:
        price = convert_price(price_string)
        item["price"] = price
        item["price_string"] = price_string
    
    try:
        image_list = []
        images = soup.find("ul",id ="ContentPlaceHolder1_ctl00_viewImage1_divLi").find_all("a")
        for image in images:
            image_url = 'https://nhadat24h.net/'+image["href"]
            image_list.append(image_url)
        item["images"] = image_list
    except:
        item["images"] = []
    
    item["description"]= soup.find("div",class_="dv-txt-mt").get_text()
    
    item["property_type"]= detail[-3].get_text()
    
    item["location"]={}
    address = detail[-2].get_text()
    item["location"]=convert_address_info(address)
    
    item["attr"] = {}
    item["attr"]["area"] =item["attr"]["total_area"]= float(area_string.split("M")[0].replace(",","."))
    try :
        item["attr"]["certificate"] = detail[1].get_text().split(":")[1]
    except:
        item["attr"]["certificate"] = detail[2].get_text().split(":")[1]

    attr = soup.find_all("div", class_="dv-tsbds")
    main_info ={}
    for i in attr:
        temp =i.find_all("td")
        if temp[1].get_text()!= '':
            main_info[temp[0].get_text()] = temp[1].get_text()
        if temp[3].get_text()!= '':
            main_info[temp[2].get_text()] = temp[3].get_text()
    try:
        if 'Mặt tiền' in main_info:
            item["attr"]["width"] = float(main_info["Mặt tiền"].split(" ")[0].replace(",","."))
        
        if 'Phòng Ngủ' in main_info:
            item["attr"]["bedroom"] = int(main_info["Phòng Ngủ"])
        
        if 'Phòng WC' in main_info:
            item["attr"]["bathroom"] = int(main_info["Phòng WC"])
        
        if 'Số tầng' in main_info:
            if item["property_type"] == 'Căn hộ chung cư':
                item['attr']["floor_num"] = int(main_info["Số tầng"].split(" ")[0])
            else:
                item["attr"]["floor"] = int(main_info["Số tầng"].split(" ")[0])
        
        if 'Hướng' in main_info:
            item['attr']["direction"] = main_info["Hướng"]
        
        if 'Mã BĐS' in main_info:
            item["attr"]["site_id"] = main_info["Mã BĐS"]
    except Exception as e:
        print('Error when parse attr', e)
        pass
            
    item["agent"] ={}
    agent_info = soup.find("div",class_="info").findAll("label")
    try:
        item["agent"]["name"] = agent_info[0].get_text()
    except:
        pass
    
    try:
        item["agent"]["agent_type"]= agent_info[1].get_text()
    except:
        pass
    
    try:
        item["agent"]["address"]=agent_info[2].get_text()
    except:
        pass
    
    try:
        item["agent"]["phone_number"]= soup.find("a",class_="call").get_text()
    except:
        pass
    
    try:
        item["agent"]["profile"] = 'https://nhadat24h.net/' + soup.find("label",class_="fullname").find("a")["href"]
    except:
        pass
    
    return item 
    
    
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

def bds68_list(url = None):
    max_num_page = 6706
    crawl_url = 'https://bds68.com.vn/nha-dat-ban?pg=1'
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
        next_page = "https://bds68.com.vn/nha-dat-ban?pg=" + str(num_cur_page + 1)
        return {'urls': urls, 'next_page': next_page}
    
    soup = BeautifulSoup(res.text, 'html.parser')
    products = soup.select(".info-line.header-prop-title h4 a[href]")
    
    # Case 1: products is not empty and current page is bigger than max_num_page
    if not products and num_cur_page > max_num_page:
        raise Exception('Crawling Finished')
    elif products:   
    #2: 200 status code and products is not empty or current page is smaller than max_num_page    
        for product in products:
            try:
                url = "https://bds68.com.vn"+ product["href"]
                urls.append(url)
            except:
                pass
    next_page = "https://bds68.com.vn/nha-dat-ban?pg=" + str(num_cur_page + 1)
    return {'urls': urls, 'next_page': next_page}

def convert_price(price):
    list_price = price.split(" ")
    sum_price = 0
    for i in range(len(list_price)):
        if list_price[i] == "tỷ":
            sum_price+= float(list_price[i-1]) * (10**9)
        elif list_price[i] == "triệu":
            sum_price+= float(list_price[i-1]) * (10**6)
    return int(sum_price)

def convert_main_info(main_info_string):
    list_info_string = main_info_string.split("\n")
    main_info={}
    for info in list_info_string:
        if info.find(":") != -1:
            key,value = info.split(":")
            main_info[key.strip()] = value.strip()
    if main_info["Giá"] == "Thỏa Thuận":
        main_info["Giá_tt"] ="Thỏa Thuận"
    else:
        main_info["Giá_tt"]= main_info["Giá"]
    return main_info

def bds68_item(url):
    
    res = requests.get(url,
                       proxies = PROXY)    
    soup = BeautifulSoup(res.text, 'html.parser')
    items = {}

    title = soup.find("h1", class_="detail-prop-title").getText().strip()
    items["title"] = title

    items['site'] = 'bds68'
    items["url"] = res.url

    images_link = []
    slides = soup.find("div",class_ = "swiper-wrapper").find_all("img")
    for slide in slides:
        try:
            images_link.append(slide["data-src"])
        except:
            pass
        try:
            images_link.append(slide["src"])
        except:
            pass
    items['images'] = images_link

    description = soup.find("div",class_ = "readmore-box").getText()
    items["description"] = description

    # 'Loại Tin Rao', 'Dự Án', 'Giá', 'Diện Tích', 'Diện Tích Sử Dụng', 'Năm xây dựng', 'Số Phòng Ngủ', 'Số Phòng Tắm', 'Đường Trước Nhà', 'Mặt Tiền', 'Số Tầng', 'Mã Đăng Tin', 'Ngày Đăng'
    main_info_string = soup.find("div", class_="prop-features").getText().replace("\r\n","")
    main_info= convert_main_info(main_info_string)
    if main_info["Giá_tt"] == "Thỏa Thuận":
        items["price_string"]= main_info["Giá_tt"]
    else:
        items["price_string"]= main_info["Giá_tt"]
        items["price"]= convert_price(main_info["Giá"])
    items["price_currency"] = "VND"

    if 'Loại Tin Rao' in main_info:
        items['property_type'] = main_info['Loại Tin Rao']
    
    if 'Ngày Đăng' in main_info:
        value = main_info["Ngày Đăng"].split("-")[0].strip()
        value = datetime.strptime(value, '%d/%m/%Y').strftime("%Y-%m-%d %H:%M:%S")
        items['publish_at'] = value      

    items["attr"]= {}
    try:
        if "Diện Tích" in main_info:
            items['attr']["area"]=float(main_info["Diện Tích"].split(" ")[0].replace(",","."))

        if 'Diện Tích Sử Dụng' in main_info:
            value = float(main_info["Diện Tích Sử Dụng"].split(" ")[0].replace(",","."))
            if items["attr"]["area"] > value:
                items["attr"]["total_area"] = items["attr"]["area"]
                items["attr"]["area"]= value
            else:
                items["attr"]["total_area"] = value
        
        if 'Năm xây dựng' in main_info:
            items["attr"]["built_year"]=int(main_info["Năm xây dựng"])

        if 'Số Phòng Ngủ' in main_info:
            items["attr"]["bedroom"]=int(main_info["Số Phòng Ngủ"])

        if 'Số Phòng Tắm' in main_info:
            items["attr"]["bathroom"] =int(main_info["Số Phòng Tắm"])
        
        if 'Mã Đăng Tin' in main_info:
            items["attr"]["site_id"] = main_info["Mã Đăng Tin"]
        
        if 'Số Tầng' in main_info:
            if items['property_type'] == "Nhà Chung Cư":
                items["attr"]["floor_num"] = int(main_info["Số Tầng"])
            else:
                items["attr"]["floor"] = int(main_info["Số Tầng"])

        if 'Mặt Tiền' in main_info:
            items["attr"]["width"] = float(main_info["Mặt Tiền"].split(" ")[0].replace(",","."))

        if 'Hướng Nhà' in main_info:
            items["attr"]["direction"]= main_info["Hướng Nhà"]
            
        if 'Dự Án' in main_info:
            items['project'] = {}
            items["project"]["name"] = main_info["Dự Án"]
            link_project = "https://bds68.com.vn"+soup.find("div", class_="prop-features").find("a")["href"]
            items["project"]["profile"]= link_project
    except Exception as e:
        print('Error when parse attr', e)
        pass
    
    try:
        features = soup.find_all("div",class_="fprop col-md-4 col-sm-6 col-xs-6")
        if len(features) != 0:
            features_str= ''
            for feature in features:
                features_str+= feature.getText().strip() +','
            items["attr"]["feature"] = features_str[:-1]
    except Exception as e:
        print('Error when parse attr', e)
        pass
    

    items["location"]= {}
    breadcumb = soup.find('div', class_="breadcrumbs").find_all("a")
    address_list = []
    address = ''
    for i in breadcumb:
        address_list.append(i.text)
    items["location"]["city"] = address_list[2]
    if len(address_list) >=4:
        items["location"]["dist"] = address_list[3]
        try:
            for i in range(len(address_list)-1,1, -1):
                if (address_list[i].find("P.") !=-1 or address_list[i].find("X.") !=-1) and i>3:
                    items["location"]["ward"]=address_list[i]
                elif address_list[i].find("Đ.") !=-1:
                    items["location"]["street"]=address_list[i]
                address+=address_list[i]+","
            items["location"]["address"] = address[:-1]
        except Exception as e:
            print('Error when parse location', e)
            pass
    
    items['agent'] = {}

    try:
        items["agent"]["name"] = soup.find("h3", class_="one-line").getText()

    except:
        pass
    
    try:
        tel = soup.find("a", class_="click_me")["href"].split(":")[1]
        items["agent"]["phone_number"] = tel
    except:
        pass

    try:
        profile = soup.find("div",class_="seller-info-container box-3d").find("a")["href"]
        items["agent"]["profile"] = 'https://bds68.com.vn'+ profile
    except:
        pass

    return items

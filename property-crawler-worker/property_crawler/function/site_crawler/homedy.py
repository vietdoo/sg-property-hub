import requests
import re
from datetime import datetime
import logging
import json
import time
# from property_crawler.items import PropertyCrawlerItem
from decimal import Decimal
from bs4 import BeautifulSoup
from .utils.config import *

def homedy_list(url = None):
    with open('property_crawler/function/site_crawler/input_data/homedy.json') as json_file:
        geodata = json.load(json_file)
    
    crawl_url ="https://homedy.com/ban-nha-dat-xa-an-phu-tay-huyen-binh-chanh-tp-ho-chi-minh/p1"
    if url:
        crawl_url=url
        
    # init variables with null or empty value
    products = []
    urls = []
    num_cur_page = int(crawl_url.split("/p")[1])
    next_page = None  

    #get city,dist,ward form crawl-url
    city_list = [key for item in geodata for key in item.keys()]
    for i in city_list:
        if i in crawl_url:
            city = i
            city_index = city_list.index(city)
    dist_list= [key for item in geodata[city_index][city] for key in item.keys()]
    for i in dist_list:
        if i in crawl_url:
            dist= i
            dist_index = dist_list.index(dist)
    ward_list= geodata[city_index][city][dist_index][dist]
    for i in ward_list:
        if i in crawl_url:
            ward= i
            ward_index = ward_list.index(ward)
            
    # Case 0: getting 403 or 404... error. Try to get next page       
    try:   
        res = requests.get(crawl_url,
                           timeout=4)
    except:
        next_page = "https://homedy.com/ban-nha-dat-{}-{}-{}/p".format(ward,dist,city) + str(num_cur_page + 1)
        return {'urls': urls, 'next_page': next_page}
    
    soup = BeautifulSoup(res.text,"html.parser")
    if soup.find("div",class_="no-result") == None:
        products = soup.find("div",class_="tab-content").find_all("h3")
        urls = []
        for product in products:
            try:
                url = "https://homedy.com" + product.find("a")["href"]
                urls.append(url)
            except:
                pass
        next_page = "https://homedy.com/ban-nha-dat-{}-{}-{}/p".format(ward,dist,city) + str(num_cur_page + 1)
        return {'urls': urls, 'next_page': next_page}
    else:
        try:
            if ward_index == len(ward_list)-1:
                ward_index =-1
                if dist_index == len(dist_list)-1:
                    dist_index = -1
                    city_index+=1
                    city = city_list[city_index]
                    dist_list= [key for item in geodata[city_index][city] for key in item.keys()]
                dist_index+=1
                dist = dist_list[dist_index]
            ward_list= geodata[city_index][city][dist_index][dist]
            ward =ward_list[ward_index+1]
            next_page = "https://homedy.com/ban-nha-dat-{}-{}-{}/p1".format(ward,dist,city) 
            return {'urls': [], 'next_page': next_page}
        except:
            raise Exception('Crawling Finished')
 
def convert_price(price):
    list_price = price.split(" ")
    sum_price = 0
    for i in range(len(list_price)):
        if list_price[i] == "Tỷ":
            sum_price+= float(list_price[i-1].replace(",",".")) * (10**9)
        elif list_price[i] == "Triệu":
            sum_price+= float(list_price[i-1].replace(",",".")) * (10**6)
    return int(sum_price)

def convert_address_info(address):
     #full string_format : "10 ngõ 55, Đường Lê Quý Đôn, Phường Bạch Đằng, Quận Hai Bà Trưng, Hà Nội"
     # convert to address,city,dist,ward,street
    info = {}
    info["address"] = address
    list_info = address.split(", ")
    list_loc = ["city","dist","ward","street"]
    for i in range(len(list_loc)):
        if len(list_info) - i -1 >= 0 :
            info[list_loc[i]] = list_info[len(list_info) - i -1].strip()
    return info
       
def homedy_item(url):
    
    res = requests.get(url,
                       proxies = PROXY)
    soup = BeautifulSoup(res.text, 'html.parser')
    item ={}
    
    title = soup.find("div",class_="product-detail-top-left").find("h1").get_text().strip()
    item["title"] = title
    
    item['site'] = 'homedy'
    item["url"] = res.url
    
    #Price
    price_string = soup.find("div",class_="product-short-info").find("strong").get_text().strip().replace("\n"," ")
    if price_string == 'Thỏa thuận':
        item["price_string"] = price_string 
    else:
        if price_string.find("- ") != -1:
            price_string = price_string.split("- ")[1]
        price = convert_price(price_string)
        item["price"] = price
        item["price_string"] = price_string
    
    image_list = []
    images = soup.find_all("a",class_="image-popup fh5co-board-img")
    for image in images:
        image_list.append(image["href"])
    item["images"]=image_list
    
    item["description"]= soup.find("div",class_="description-content").get_text().strip()
    
    #Main Info 
    main_info = {}
    main_info_string = soup.find("div",class_="product-attributes").find_all("div")

    for i in main_info_string:
        temp = i.find_all("span")
        main_info[temp[0].get_text()] = temp[1].get_text()
    
    item["property_type"] = main_info["Loại hình"]
    
    detail = soup.find("div",class_="product-info").find_all("div")

    date = detail[0].find("p",class_="code").get_text().strip()
    
    item["publish_at"] = datetime.strptime(date, "%d/%m/%Y").strftime("%Y-%m-%d %H:%M:%S")
    
    address = soup.find("div",class_="address").get_text().rsplit("-",1)[1].strip()
    item["location"] = convert_address_info(address)
    
    item["attr"]= {}
    area = soup.find("div",class_="product-short-info").find_all("strong")[1].get_text().strip()
    if area != '--':
        if area.find("- ") != -1:
            area = area.split("- ")[1]
        item["attr"]["area"] = float(area.split("\n")[0].replace(",","."))
        item["attr"]["total_area"]=float(area.split("\n")[0].replace(",","."))
    try:
        if 'Số phòng ngủ' in main_info:
            item["attr"]["bedroom"] = int(main_info["Số phòng ngủ"])
            
        if 'Hướng nhà' in main_info:
            item["attr"]["direction"] = main_info["Hướng nhà"]
        
        if 'Tình trạng pháp lý' in main_info:
            item["attr"]["certificate"] = main_info["Tình trạng pháp lý"]
        
        if 'Số tầng' in main_info:
            if item["property_type"] == 'Căn hộ':
                
                item["attr"]["floor_num"] = main_info["Số tầng"]
            else:
                item["attr"]["floor"] = main_info["Số tầng"]
        
    except Exception as e:
        print('Error when parse attr', e)
        pass
    
    try:
        interiors =  soup.find("div",class_="product-properties").find_all("div",class_="item")
        interior = ''
        for i in interiors:
            interior+= i.get_text().strip()+','
        item["attr"]["interior"] = interior[:-1]
    except:
        pass
    
    item["agent"] = {}
    
    try:
        item["agent"]["name"] = soup.find("div",class_="name").get_text().strip()
    except:
        pass
    try:
        item["agent"]["profile"] ='https://homedy.com' + soup.find("div",class_="name").find("a")["href"]
    except:
        pass
    
    try:
        item["agent"]["phone_number"] = soup.find("a",class_="btn tooltip right pc-mobile-number mobile mobile-counter mobile-box")["data-mobile"]
    except:
        pass
    return item
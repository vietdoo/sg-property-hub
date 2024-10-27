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

def bds123_list(url = None):
    max_num_page = 7282
    crawl_url = 'https://bds123.vn/nha-dat-ban.html?page=1'
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
        next_page = "https://bds123.vn/nha-dat-ban.html?page=" + str(num_cur_page + 1)
        return {'urls': urls, 'next_page': next_page}
    
    soup = BeautifulSoup(res.text, 'html.parser')
    list_product= soup.find("ul",class_="post-listing")
    
    # Case 1: products is not empty and current page is bigger than max_num_page
    if not list_product and num_cur_page > max_num_page:
        raise Exception('Crawling Finished')
    elif list_product:
    #2: 200 status code and products is not empty or current page is smaller than max_num_page
        products = list_product.find_all("a")
        for product in products:
            try:
                url = "https://bds123.vn"+ product["href"]
                urls.append(url)
            except:
                pass
    next_page = "https://bds123.vn/nha-dat-ban.html?page=" + str(num_cur_page + 1)
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
    
def convert_area_info(area_string):
    #full string_format : "1.200,1 m² (3,5x11,0)"" convert to total_area,width,length
    info = {}
    list_info = area_string.split(" m2")
    total_area = float(list_info[0].replace(".","").replace(",","."))
    info["total_area"] =info["area"]= total_area
    if list_info[-1]  !=  '':
        wid_len = list_info[1].split(" x ")
        width = float(wid_len[0].replace("(","").replace(",","."))
        length= float(wid_len[1].replace(")","").replace(",","."))
        if width > length:  
            width,length = length,width
        info["width"]=width
        info["length"]=length
    return info

def bds123_item(url):
    
    res = requests.get(url,
                       proxies = PROXY)    
    soup = BeautifulSoup(res.text, 'html.parser')
    item = {}
    
    title = soup.find("h1",class_="page-h1").get_text().strip()
    item["title"] = title
    
    item["site"] = 'bds123'
    item["url"] = res.url
    
    price_string = soup.find("span",class_="item post-price").get_text().strip()
    if price_string == 'Thỏa thuận':
        item["price_string"] = price_string 
    else:
        price = convert_price(price_string)
        item["price"] = price
        item["price_string"] = price_string
    
    img_doc =soup.find("div",class_="leftCol").find_all("div")[0]
    try:
        images_list = [img["data-src"] for img in img_doc.find_all("img")]
    except:
        images_list = []
    item["images"] = images_list
    
    description = soup.find_all("div",class_="post-section margin-bottom-30")[1].get_text()
    item["description"] = description[15:] #delete 'Thông tin mô tả' at head
    
    breadcrumb =soup.find("div",id="breadcrumb").find_all("li")
    property = breadcrumb[1].get_text()
    item["property_type"] = property.replace("Bán ","")
    
    detail_doc = soup.find("table",class_="table-overview").find_all("td")
    if len(detail_doc)>10:
        date = detail_doc[9].get_text().split(", ")[1]
    else:
        date = detail_doc[7].get_text().split(", ")[1]
    item["publish_at"]= datetime.strptime(date, "%H:%M %d/%m/%Y").strftime("%Y-%m-%d %H:%M:%S")
    
    item["location"] = {}
    city = breadcrumb[2].get_text().replace(property+" ","")
    item["location"]["city"] = city
    
    dist = breadcrumb[3].get_text().replace(property+" ","")
    item["location"]["dist"] = dist
    
    address = soup.find("p",class_="item post-address").find("span").get_text()
    item["location"]["address"] = address.split(": ")[1]
    
    item["attr"]={}
    try:
        area = soup.find("span", class_="item post-acreage").get_text()
        item["attr"].update(convert_area_info(area))
    except:
        pass
    
    try:
        bedroom = soup.find("span", class_="item post-bedroom").get_text().strip()
        item["attr"]["bedroom"] = int(bedroom.split(" ")[0])
    except:
        pass
    try:
        bathroom = soup.find("span", class_="item post-bathroom").get_text().strip()
        item["attr"]["bathroom"]=int(bathroom.split(" ")[0])
    except:
        pass
    try:
        direction = soup.find("span",class_="item post-direction").get_text()
        item["attr"]["direction"]= direction
    except:
        pass
    try:
        id = detail_doc[1].get_text()
        item["attr"]["site_id"]= id
    except:
        pass
    
    item["agent"]={}
    try:
        item["agent"]["name"] = soup.find("div",class_="author-name").get_text()
    except:
        pass
    try:
        item["agent"]["phone_number"]=soup.find("button",class_="btn btn-phone").get_text().strip()
    except:
        pass
    try:
        item["agent"]["profile"]=soup.find("a",class_="author-url-wrap d-flex clearfix")["href"]
    except:
        pass
    
    item["project"]={}
    try:
        if len(breadcrumb) ==5:
            project_name = breadcrumb[4].get_text()
            item["project"]["name"]= project_name.replace(property+" ","")
            profile = breadcrumb[4].find("a")["href"]
            item["project"]["profile"]="https://bds123.vn"+ profile
    except:
        pass
    return item
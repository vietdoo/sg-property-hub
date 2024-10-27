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

def muaban_list(url = None):
    max_offset= 102860
    
    crawl_url = "https://muaban.net/listing/v1/classifieds/listing?subcategory_id=169&category_id=33&limit=20&offset=0"
    if url:
        crawl_url=url
        
    # init variables with null or empty value
    products = []
    urls = []
    num_offset = int(crawl_url.split("offset=")[1])
    next_page = None
    
    # Case 0: getting 403 or 404... error. Try to get next page
    try:
        res = requests.get(crawl_url,
                           timeout=4)
    except:
        next_page = "https://muaban.net/listing/v1/classifieds/listing?subcategory_id=169&category_id=33&limit=20&offset="+str(num_offset +20)
        return {'urls': urls, 'next_page': next_page}        
    
    products = res.json()
    
    # Case 1: products is not empty and current page is bigger than max_num_page
    if not products["items"] and num_offset > max_offset:
        raise Exception('Crawling Finished')
    elif products["items"]:
    #2: 200 status code and products is not empty or current page is smaller than max_num_page
        for product in products["items"]:
            try:
                url = "https://muaban.net/"+product["url"]
                urls.append(url)
            except:
                pass
    next_page = "https://muaban.net/listing/v1/classifieds/listing?subcategory_id=169&category_id=33&limit=20&offset="+str(num_offset +20)
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

def convert_area_info(area_string):
    #full string_format : "1.200,1 m² (3,5x11,0)"" convert to total_area,width,length
    info = {}
    list_info = area_string.split(" ")
    total_area = float(list_info[0].replace(".","").replace(",","."))
    info["total_area"] =info["area"]= total_area
    if len(list_info) > 2:
        wid_len = list_info[2].split("x")
        width = float(wid_len[0].replace("(","").replace(",","."))
        length= float(wid_len[1].replace(")","").replace(",","."))
        if width > length:  
            width,length = length,width
        info["width"]=width
        info["length"]=length
    return info
    
def muaban_item(url):
    
    id = int(url.split("id")[1])
    api_url =f"https://muaban.net/listing/v1/classifieds/{id}/detail"
    res = requests.get(api_url,
                       proxies = PROXY)
    data = res.json()
    item ={}
    
    item["title"]=data['title']
    
    item["url"] = "https://muaban.net/"+ data['url']
    
    item["site"] = 'muaban'
    
    item["price"] = data['price']
    
    #item["price_string"] = data['price_display'].replace(".","")
    item["price_string"] = data['price_display']
    
    images_link=[]
    for image in data["images"]:
        images_link.append(image["url"])
    item['images'] = images_link
    
    item["description"] = data['body']
    
    date = data["publish_at"].split(".")[0].replace("T"," ")
    item["publish_at"] = date
    
    item["location"] = convert_address_info(data['address'])
    
    #'Loại hình nhà ở', 'Dự án', 'Diện tích đất', 'Số phòng ngủ', 'Số phòng vệ sinh', 'Tổng số tầng', 'Hướng cửa chính', 'Hướng ban công', 'Giấy tờ pháp lý', 'Điểm nổi bật'
    #{'Loại hình nhà ở': 'Biệt thự, Villa', 'Dự án': 'KBT Vườn Cọ Palm Garden', 'Diện tích đất': '205,5 m² (10,0x20,5)', 'Số phòng ngủ': '5 phòng', 'Số phòng vệ sinh': '4 WC', 'Tổng số tầng': '3', 'Hướng cửa chính': 'Đông Nam', 'Hướng ban công': 'Tây Bắc', 'Giấy tờ pháp lý': 'Sổ đỏ', 'Điểm nổi bật': '<ul><li>Giao nhà ngay</li></ul>'}
    main_info = {}
    for i in data['parameters']:
        main_info[i["label"]] = i["value"]
    
    if 'Loại hình nhà ở' in main_info:
        item["property_type"] = main_info['Loại hình nhà ở']
    if 'Loại hình đất' in main_info:
        item["property_type"] = main_info['Loại hình đất']
    if 'Loại hình căn hộ' in main_info:
        item["property_type"] = main_info['Loại hình căn hộ']
        
    item["attr"] = {} 
    item["attr"]["site_id"] = data['id']
    try:
        if 'Diện tích đất' in main_info:
            item["attr"].update(convert_area_info(main_info['Diện tích đất']))
        
        if 'Diện tích sử dụng' in main_info:
            item["attr"].update(convert_area_info(main_info['Diện tích sử dụng']))
        
        if 'Số phòng ngủ' in main_info:
            item["attr"]["bedroom"] = int(main_info["Số phòng ngủ"].split(" ")[0])
        
        if 'Số phòng vệ sinh' in  main_info:
            item["attr"]["bathroom"]= int(main_info["Số phòng vệ sinh"].split(" ")[0])
        
        if 'Tổng số tầng' in main_info:
            item["attr"]["floor"] = int(main_info["Tổng số tầng"])
        
        if 'Tầng số' in main_info:
            item["attr"]["floor_num"]=int(main_info["Tầng số"].split("/")[0])
        
        if 'Hướng cửa chính' in main_info:
            item["attr"]["direction"] = main_info["Hướng cửa chính"]
        
        if 'Giấy tờ pháp lý' in main_info:
            item["attr"]["certificate"] = main_info['Giấy tờ pháp lý']
        
        if 'Điểm nổi bật' in main_info:
            #item["attr"]["feature"] = main_info['Điểm nổi bật'].replace("</li><li>",",").replace("</li></ul>","").replace("<ul><li>","")
            item["location"]["description"] = main_info['Điểm nổi bật']
            
        if 'Dự án' in main_info:
            item["project"] = {}
            item["project"]["name"] = main_info["Dự án"]
            try:
                project_url = "https://muaban.net"+ data["breadcrumbs"][5]["url"]
                item["project"]["profile"] = project_url
            except Exception as e:
                print('Error when parse project', e)
                pass
    except Exception as e:
        print('Error when parse attr', e)
        pass
        
    item["agent"] = {}
    try:
        item["agent"]["name"]= data['contact_name']
    except Exception as e:
        print('Error when parse agent', e)
        pass
    try:
        item["agent"]["phone_number"] = data['phone']
    except Exception as e:
        print('Error when parse agent', e)
        pass
    try:
        agent_profile = "https://muaban.net/trang-ca-nhan/" + str(data['user_id'])
        item["agent"]["profile"] = agent_profile
    except: 
        pass
    return item
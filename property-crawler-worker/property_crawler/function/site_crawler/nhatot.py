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
import os

def nhatot_list(url = None):
    with open('property_crawler/function/site_crawler/input_data/nhatot.json') as json_file:
        json_data = json.load(json_file)
    geo,region_idx,idx_region= json_data

    crawl_url = 'https://gateway.chotot.com/v1/public/ad-listing?st=s,k&limit=100&o=0&cg=1000&region_v2=13000&area_v2=13119&key_param_included=true'
    if url:
        crawl_url = url
    # init variables with null or empty value
    products = []
    urls = []
    next_page = None 
    limit = int(crawl_url.split("&limit=")[1].split("&")[0])
    o = int(crawl_url.split("&o=")[1].split("&")[0])
    region = crawl_url.split("&region_v2=")[1].split("&")[0]
    area = crawl_url.split("&area_v2=")[1].split("&")[0]
    
    
     # Case 0: getting 403 or 404... error. Try to get next page
    try:   
        res = requests.get(crawl_url,timeout=4)
    except:
        new_o = o + limit
        next_page = f'https://gateway.chotot.com/v1/public/ad-listing?st=s,k&limit=100&o={str(new_o)}&cg=1000&region_v2={region}&area_v2={area}&key_param_included=true'
        return {'urls': urls, 'next_page': next_page}    
    products = res.json()
    
    if products["ads"]:
    #2: 200 status code and products is not empty or current page is smaller than max_num_page
        for product in products["ads"]:
            try:
                url = f'https://www.nhatot.com/{product["list_id"]}.htm'
                urls.append(url)
            except:
                pass
        new_o = o + limit
        next_page = f'https://gateway.chotot.com/v1/public/ad-listing?st=s,k&limit=100&o={str(new_o)}&cg=1000&region_v2={region}&area_v2={area}&key_param_included=true'
        return {'urls': urls, 'next_page': next_page}
    else:
        list_dist = geo[region]
        try:
            idx = list_dist.index(area)
            if idx == (len(list_dist)-1):
                region_id = region_idx[region]
                new_region = idx_region[str(region_id+1)]
                new_list_dist = geo[new_region]
                new_area = new_list_dist[0]
                next_page= f'https://gateway.chotot.com/v1/public/ad-listing?st=s,k&limit=100&o=0&cg=1000&region_v2={new_region}&area_v2={new_area}&key_param_included=true'

            else:
                new_area = list_dist[idx+1]
                next_page = f'https://gateway.chotot.com/v1/public/ad-listing?st=s,k&limit=100&o=0&cg=1000&region_v2={region}&area_v2={new_area}&key_param_included=true'
            return {'urls': [], 'next_page': next_page}
        except:
            raise Exception('Crawling Finished')
        
def nhatot_item(url):
    
    id = url.split(".com/")[1].split(".")[0]

    api_url = f"https://gateway.chotot.com/v2/public/ad-listing/{id}?adview_position=true&tm=treatment2"
    res = requests.get(api_url,
                       proxies = PROXY)
    data = res.json()
    item ={}
    
    item["title"] = data["ad"]['subject']
    
    item["url"] = "https://www.nhatot.com/{}.htm".format(data["ad"]["list_id"])
    
    item["site"] = 'nhatot'
    
    item["price"] = data["ad"]['price']
    
    item["price_string"]= data["ad"]['price_string']
    
    if 'images' in data["ad"]:
        item['images'] = data["ad"]["images"]
    else:
        item['images'] = []
    
    item["description"]= data["ad"]["body"]
    
    item["property_type"]= data["ad"]["category_name"]
    
    time_value = data["ad"]["list_time"] #/1000 to convert ms to s
    item["publish_at"] = datetime.fromtimestamp(time_value/1000).strftime("%Y-%m-%d %H:%M:%S")
    
    attr_data = {}
    for info in data["parameters"]:
        try:
            attr_data[info["label"]] = info["value"]
        except:
            continue
    
    item["location"] = {}
    item["location"]["city"] = data["ad"]["region_name"]
    
    item["location"]["dist"] = data["ad"]["area_name"]
    try:
        item["location"]["address"]= attr_data["Địa chỉ"]
    except:
        pass
    try:
        item["location"]["ward"]= data["ad"]["ward_name"]
    except:
        pass
    try:
        item["location"]["street"]= data["ad"]["street_name"]
    except:
        pass
    try:
        item["location"]["long"]= data["ad"]["longitude"]
    except:
        pass
    try:    
        item["location"]["lat"]= data["ad"]["latitude"]
    except:
        pass  
    
    item["attr"]={}
    item["attr"]['site_id'] = str(data["ad"]["list_id"])
    
    try:
        if 'Diện tích' in attr_data:
            item["attr"]["area"] = float(attr_data["Diện tích"].split(" ")[0])
            
        if 'Diện tích đất' in attr_data:
            item["attr"]["area"] = float(attr_data["Diện tích đất"].split(" ")[0])
        
        if 'Diện tích sử dụng' in attr_data:
            value = float(attr_data["Diện tích sử dụng"].split(" ")[0])
            if item["attr"]["area"] > value:
                item["attr"]["total_area"] = item["attr"]["area"]
                item["attr"]["area"]= value
            else:
                item["attr"]["total_area"] = value
        
        if 'Chiều ngang' in attr_data:
            item["attr"]["width"] = float(attr_data['Chiều ngang'].split(" ")[0])
            
        if 'Chiều dài' in attr_data:
            item["attr"]["length"] = float(attr_data['Chiều dài'].split(" ")[0])
        
        if 'Số phòng ngủ' in attr_data: #nhieu hon 10
            list_info = attr_data['Số phòng ngủ'].split(" ")
            if len(list_info) == 2:
                item["attr"]["bedroom"] = int(list_info[0])
            else:
                item["attr"]["bedroom"] = int(list_info[2])
                
        if 'Số phòng vệ sinh' in attr_data: # nhieu hon 6
            list_info = attr_data['Số phòng vệ sinh'].split(" ")
            if len(list_info) == 2:
                item["attr"]["bedroom"] = int(list_info[0])
            else:
                item["attr"]["bedroom"] = int(list_info[2])
        
        if 'Tổng số tầng' in attr_data:
            item["attr"]["floor"] = int(attr_data["Tổng số tầng"])
        
        if 'Tầng số' in attr_data:
            item["attr"]["floor_num"] = int(attr_data["Tầng số"])
        
        if 'Hướng cửa chính' in attr_data:
            item["attr"]['direction'] = attr_data["Hướng cửa chính"]
        
        if 'Tình trạng nội thất' in attr_data:
            item["attr"]['interior'] = attr_data["Tình trạng nội thất"]
        
        if 'Đặc điểm nhà/đất' in attr_data:
            item["location"]["description"] = attr_data["Đặc điểm nhà/đất"]
            
        if 'Đặc điểm căn hộ' in attr_data:
            item["location"]["description"] = attr_data["Đặc điểm căn hộ"]
            
        if 'Loại hình nhà ở' in attr_data:
            item["attr"]['type_detail'] = attr_data["Loại hình nhà ở"]
        
        if 'Loại hình căn hộ' in attr_data:
            item["attr"]['type_detail'] = attr_data["Loại hình căn hộ"]
        
        if 'Loại hình đất' in attr_data:
            item["attr"]['type_detail'] = attr_data["Loại hình đất"]
            
        if 'Loại hình văn phòng' in attr_data:
            item["attr"]['type_detail'] = attr_data["Loại hình văn phòng"]
        
        if 'Giấy tờ pháp lý' in attr_data:
            item["attr"]['certificate'] = attr_data["Giấy tờ pháp lý"]
        
        if 'Tình trạng bất động sản' in attr_data:
            item["attr"]['condition'] = attr_data["Tình trạng bất động sản"]

    except Exception as e:
        print('Error when parse attr', e)
        pass
    
    item["agent"]={}
    try:
        item["agent"]["name"] = data["ad"]["account_name"]
    except Exception as e:
        print('Error when parse agent', e)
        pass
    try:
        profile='https://www.chotot.com/user/{}'.format(data["ad"]["account_oid"])
        item["agent"]["profile"] = profile
    except Exception as e:
        print('Error when parse agent', e)
        pass
    
    if 'project_oid' in data["ad"]:
        item["project"]={}
        try:
            crawl_url = 'https://gateway.chotot.com/v1/public/api-pty/project/'+data["ad"]["project_oid"]
            project_res = requests.get(crawl_url)
            project_data = project_res.json()
            item["project"]["name"] = project_data["project_name"]
            item["project"]["profile"] = project_data["web_url"]
        except Exception as e:
            print('Error when parse project', e)
            pass
        
    return item
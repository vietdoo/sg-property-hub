import requests
import re
from datetime import datetime
import logging
import json
# from property_crawler.items import PropertyCrawlerItem
from decimal import Decimal
from bs4 import BeautifulSoup
import time
import re
from .utils.config import *

def batdongsanonline_list(url = None):
    max_num_page = 3392
    crawl_url = 'https://batdongsanonline.vn/mua-ban-dat/?page=1'
    if url:
        crawl_url = url
    # init variables with null or empty value
    products = []
    urls = []
    num_cur_page = int(crawl_url.split("=")[1])
    next_page = None  
    types = ["mua-ban-dat","mua-ban-nha","mua-ban-biet-thu","ban-can-ho-chung-cu"]
    type = crawl_url.split("vn/")[1].split("/?")[0]
    # Case 0: getting 403 or 404... error. Try to get next page
    try:   
        res = requests.get(crawl_url,
                           timeout=4)
    except:
        next_page = "https://bds68.com.vn/nha-dat-ban?page=" + str(num_cur_page + 1)
        return {'urls': urls, 'next_page': next_page}

    soup = BeautifulSoup(res.text, 'html.parser')
    products = soup.find_all("div",class_="info_td_bds w7")

    if products:
        for product in products:
            try:
                url = "https://batdongsanonline.vn/"+ product.find("a")["href"]
                urls.append(url)
            except:
                pass
        next_page = "https://batdongsanonline.vn/{}/?page=".format(type) + str(num_cur_page + 1)
        return {'urls': urls, 'next_page': next_page}
    else:
        idx = types.index(type)
        if idx < len(types)-1:
            next_page = 'https://batdongsanonline.vn/{}/?page=1'.format(types[idx+1])
            return {'urls': [], 'next_page': next_page}
        else:
            raise Exception('Crawling Finished')

def convert_price(price,soup):
    list_price = price.split(" ")
    sum_price = 0
    for i in range(len(list_price)):
        if list_price[i] == "tỷ":
            sum_price+= float(list_price[i-1].replace(",",".")) * (10**9)
        elif list_price[i] == "triệu":
            sum_price+= float(list_price[i-1].replace(",",".")) * (10**6)
        elif list_price[i] == "Triệu/m2":
            area = soup.find_all("span",class_="sp2")[1].get_text().strip()
            sum_price += float(list_price[i-1].replace(",",".")) * (10**6) * float(area.split(" ")[0].replace(",","."))
        elif list_price[i] == "Triệu/sào":
            sum_price += float(list_price[i-1].replace(",",".")) * (10**6) * 1000
        elif list_price[i] == "Triệu/Tháng":
            raise Exception("Triệu/Tháng??????")
    return int(sum_price)

def convert_main_info(main_info_doc):
    main_info ={}
    for info in main_info_doc:
        if info.find("span").get_text() == ' Đặc điểm nổi bật':
            feature = ",".join(i.get_text() for i in info.find_all("li",class_="childen"))
            main_info["Đặc điểm nổi bật"] = feature
            break
        else:
            main_info[info.find("span").get_text().strip()] = info.find("div",class_="text-right fr").get_text()
    return main_info


def batdongsanonline_item(url):
    
    res = requests.get(url,
                       proxies = PROXY)
    soup = BeautifulSoup(res.text, 'html.parser')
    item ={}
    
    title= soup.find("h1",class_="title_D").get_text()
    item["title"] = title
    
    item['site'] = 'batdongsanonline'
    item["url"] = res.url
    
    price_string = soup.find("span",class_="amount cl-red sp2").get_text().strip()
    if price_string == 'Thương lượng':
        item["price_string"] = price_string 
    else:
        price = convert_price(price_string,soup)
        item["price"] = price
        item["price_string"] = price_string
    
    try:
        img_doc = soup.find("div",class_="jumpto-block pt-2")
        img_str = re.search(r'images: (\[.*\])', img_doc.find_all("script")[1].text).group(1)
        images = eval(img_str)
        images_list=[image.replace("\/","/") for image in images]
        item["images"] = images_list
    except Exception as e:
        print('Error when parse image', e)
        pass
    
    item["description"]= soup.find("div",class_="jumpto-block1").get_text().strip()
    
    breacrum = soup.find("ul",class_="ul-breacrum").find_all("span")
    item["property_type"]=breacrum[1].get_text().replace("Mua bán ","")
    
    detail = soup.find_all("div",class_="col-md-4 col-6 p-0")
    date = detail[1].get_text().split(": ")[1].strip()
    item["publish_at"] = datetime.strptime(date, '%d/%m/%Y').strftime("%Y-%m-%d %H:%M:%S")
    
    item["location"] ={}
    item["location"]["city"]= breacrum[2].get_text()
    try:
        item["location"]["dist"]=breacrum[3].get_text()
    except Exception as e:
        raise Exception(e)
    try:
        item["location"]["ward"] = breacrum[4].get_text()
    except:
        pass
    try:
        item["location"]["address"] = soup.find("p",class_="Viethoa1").get_text()
    except:
        pass
    
    item["attr"] = {}
    area = soup.find_all("span",class_="sp2")[1].get_text().strip()
    item["attr"]["area"]=item["attr"]["total_area"]= float(area.split(" ")[0].replace(",","."))
    item["attr"]["site_id"]=detail[0].get_text().split(": ")[1].strip()
    try:
        main_info_doc= soup.find("div",id="tab-info").find_all("li")
        main_info = convert_main_info(main_info_doc)
        if 'Chiều ngang' in main_info:
            item["attr"]["width"] = float(main_info["Chiều ngang"].replace("m","").replace(",","."))
            
        if 'Chiều dài' in main_info:
            item["attr"]["length"] = float(main_info["Chiều dài"].replace("m","").replace(",","."))
            
        if 'Hướng đất' in main_info:
            item["attr"]["direction"] = main_info["Hướng đất"]
            
        if 'Hướng cửa chính' in main_info:
            item["attr"]["direction"] = main_info["Hướng cửa chính"]
            
        if 'Pháp lý' in main_info:
            item["attr"]["certificate"] = main_info["Pháp lý"]
            
        if 'Tình trạng' in main_info:
            item["attr"]["condition"] = main_info["Tình trạng"]
            
        if 'Tình trạng BDS' in main_info:
            item["attr"]["condition"] = main_info["Tình trạng BDS"]
            
        if 'Số phòng ngủ' in main_info:
            item["attr"]["bedroom"] = int(main_info["Số phòng ngủ"].split(" ")[0])
            
        if 'Số phòng vệ sinh' in main_info:
            item["attr"]["width"] = int(main_info["Số phòng vệ sinh"].split(" ")[0])
            
        if 'Nội thất' in main_info:
            item["attr"]["interior"] = main_info["Nội thất"]
            
        if 'Kiểu bất động sản' in main_info:
            item["attr"]["type_detail"] = main_info["Kiểu bất động sản"]
            
        if 'Tổng số tầng' in main_info:
            item["attr"]["floor"] = int(main_info["Chiều ngang"])
        
        if 'Tầng số' in main_info:
            item["attr"]["floor_num"]= int(main_info["Tầng số"])
            
        if 'Đặc điểm nổi bật' in main_info:
            item["attr"]["feature"] = main_info["Đặc điểm nổi bật"]
            
    except Exception as e:
        print('Error when parse attr', e)
        pass
    
    item["agent"]={}
    try:
        name = soup.find("div",class_="our_sb").find("span",class_="name").getText().strip()
        item["agent"]["name"] = name
    except:
        pass
    
    try:
        phone = soup.find("div",class_="our_sb").find("a",class_="tag-phone")["data-phone"]
        item["agent"]["phone_number"] = phone
    except:
        pass
    
    try:
        profile = "https://batdongsanonline.vn"+ soup.find("div",class_="our_sb").find_all("a")[-1]["href"]
        item["agent"]["profile"] = profile
    except:
        pass
    
    return item
    
        
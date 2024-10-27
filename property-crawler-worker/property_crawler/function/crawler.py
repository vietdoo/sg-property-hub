from .site_crawler.nhadat24h import (
    nhadat24h_item, nhadat24h_list)
from .site_crawler.houseviet import (
    houseviet_item, houseviet_list
)
import pytz
from datetime import date, datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, validator
from pydantic.networks import HttpUrl

from .site_crawler.mogi import (
    mogi_item, mogi_list)
from .site_crawler.bds68 import (
    bds68_item, bds68_list)
from .site_crawler.muaban import (
    muaban_item, muaban_list)
from .site_crawler.nhatot import (
    nhatot_item, nhatot_list)
from .site_crawler.batdongsan_so import (
    batdongssan_so_item, batdongssan_so_list)
from .site_crawler.ibatdongsan import (
    ibatdongsan_item, ibatdongsan_list)
from .site_crawler.batdongsanonline import(
    batdongsanonline_item,batdongsanonline_list)
from .site_crawler.bds123 import(
    bds123_item,bds123_list)
from.site_crawler.w123nhadatviet import(
    w123nhadatviet_item,w123nhadatviet_list)
from .site_crawler.homedy import(
    homedy_item,homedy_list)
from .site_crawler.raovat import(
    raovat_item,raovat_list)
from .site_crawler.meeyland import(
    meeyland_item, meeyland_list)


class LocationModel(BaseModel):
    city: str
    dist: str
    ward: str = None
    street: str = None
    long: float = None
    lat: float = None       
    address: str = None     #address of house
    description: str = None #description of location: gan truong hoc, gan benh vien, hem xe hoi, ...

class AttrModel(BaseModel):
    area: float = None      #area of house: dien tich dat, dien tich 1 san, ...
    total_area: float = None #total area of house: dien tich su dung, dien tich toan bo san, ...
    width: float = None     #width of house: 5
    length: float = None    #length of house: 20
    height: float = None    #height of house: 10
    total_room: int = None  #number of room: 5 | if total_room > n then total_room = n
    bedroom: int = None     #number of bedroom: 3 | if bedroom > n then bedroom = n
    bathroom: int = None    #number of bathroom: 2 | if bathroom > n then bathroom = n
    floor: float = None     #number of floor: 5  | if floor > n then floor = n
    floor_num: float = None #floor number [aparment or something like that]: 19
    direction: str = None   #direction of house
    interior: str = None    #everything related to interior
    feature: str = None     #everything related to feature: pool, garden, ...
    type_detail: str = None #everything related to type_detail: shophouse, ...
    certificate: str = None #certificate of house: so hong, vi bang, ...
    built_year: int = None  #year of house built
    condition: str = None   #condition of house: new, old, ...
    site_id: str = None     #id of item in site

class AgentModel(BaseModel):
    name: str = None
    agent_type: str = None  #type of agent: owner, agent, cong ty bds...
    phone_number: str = None
    email: str = None       #email of agent
    address: str = None     #address of agent
    profile: str = None     #link to agent profile
    

class ProjectModel(BaseModel):
    name: str = None        #name of project
    profile: str = None     #link to project profile

#EVERTHING SHOULD BE IN RAW FORMAT
class PropertyCrawlerItem(BaseModel):
    id: str
    title: str
    url: HttpUrl
    site: str
    price: int = None
    price_currency: str = 'VND'
    price_string: str
    images: List[HttpUrl] = []  
    thumbnail: HttpUrl = None #automatic create thumbnail
    description: str
    property_type: str 
    # property_type: Literal['apartment', 'house', 'land', 'shop']
    publish_at: str = None
    initial_at: str
    update_at: str
    location: LocationModel
    attr: AttrModel
    agent: Optional[AgentModel]
    project: ProjectModel = None


def validate_item(item, is_raw=True):
    '''Validate item

    Args:
        item (dict): Item to validate

    Raises:
        Exception: Validation failed
    '''
    return PropertyCrawlerItem(**item)


crawler = {
    'mogi': {
        'list': mogi_list,
        'item': mogi_item,
    },
    'bds68':{
        'list': bds68_list,
        'item': bds68_item,
    },
    'muaban':{
        'list': muaban_list,
        'item': muaban_item,
    },
    'nhatot':{
        'list': nhatot_list,
        'item': nhatot_item,
    },
    'batdongsan_so':{
        'list': batdongssan_so_list,
        'item': batdongssan_so_item,
    },
    'ibatdongsan':{
        'list': ibatdongsan_list,
        'item': ibatdongsan_item,
    },
    'batdongsanonline':{
        'list': batdongsanonline_list,
        'item': batdongsanonline_item
    },
    'bds123':{
        'list': bds123_list,
        'item': bds123_item
    },
    'w123nhadatviet':{
        'list':w123nhadatviet_list,
        'item':w123nhadatviet_item
    },
    'nhadat24h':{
        'list':nhadat24h_list,
        'item':nhadat24h_item
    },
    'houseviet':{
        'list':houseviet_list,
        'item':houseviet_item
    },
    'homedy':{
        'list':homedy_list,
        'item':homedy_item
    },
    'raovat':{
        'list':raovat_list ,
        'item':raovat_item
    },
    'meeyland': {
        'list': meeyland_list,
        'item': meeyland_item
    }
    
}

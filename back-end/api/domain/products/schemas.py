from pydantic import BaseModel

class ProductsFilter(BaseModel):
    limit: int 
    category: str 
    dist: str
    city: str
    q: str 
    lowest_price: int 
    highest_price: int 
    lat_tl: float
    long_tl: float
    lat_br: float 
    long_br: float 
    offset: int 

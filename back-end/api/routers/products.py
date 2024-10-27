from . import router, SessionLocal, func, House, Location, Attr, Agent, Project, Property, PriceAVG, not_
import json
from fastapi import Query, HTTPException

@router.get("/api/products")
def get_products(
    #  fields: str = Query(...),
    limit: int = Query(24),
    category: str = Query(None, max_length=50),
    dist: str = Query(None, max_length=50),
    city: str = Query(None, max_length=50),
    q: str = Query(None),
    lowest_price: int = Query(None),
    highest_price: int = Query(None),
    lat_tl: float = Query(None),
    long_tl: float = Query(None),  
    lat_br: float = Query(None),
    long_br: float = Query(None),
    offset: int = Query(0),
    #  sort_by: str = Query(None)
):
    try:
        db = SessionLocal()
        query = db.query(Property)
    
        if category:
            query = query.filter(Property.property_type == category)

        if dist:
            query = query.filter(Property.location_dist == dist)
        
        if city:
            query = query.filter(Property.location_city == city)
           
        if q:
            query = query.filter(Property.title.like(f"%{q}%"))
        
        if lat_tl and lat_br and long_tl and long_br:
            query = query.filter(Property.location_lat >= lat_br).filter(Property.location_lat <= lat_tl)
            query = query.filter(Property.location_long >= long_tl).filter(Property.location_long <= long_br)    

        excluded_sites = ['123nhadatviet', 'i-batdongsan']
        query = query.filter(not_(Property.site.in_(excluded_sites)))
        
        query = query.filter(Property.price.isnot(None))
        query = query.filter(func.length(Property.image) > 15)
            
        if lowest_price:
            query = query.filter(Property.price>= lowest_price)
        
        if highest_price:
            query = query.filter(Property.price<= highest_price)   
        

        query = query.offset(offset)
        query = query.limit(limit)
         
        data = query.all()
        
        if not data:
            raise HTTPException(status_code=404, detail="Item not found")
        
        for item in data:
            tmp_image = item.image.strip("[]").split(",")
            image = []
            for img in tmp_image:
                if len(img) > len('https://cnd.vdcent'):
                    image.append(img.strip())
                
            item.image = image
            
                    
        return data
    except Exception as e:
        print("Error when get products: ",e)

@router.get("/api/product")
def get_product(id: str = Query(None, max_length = 50)):
    try:
        db = SessionLocal()
        print(db)
        query = db.query(Property)
        query = query.filter(Property.price.isnot(None))
        query = query.filter(Property.id == id)

        product = query.one_or_none()
        if not product:
            raise HTTPException(status_code = 404, detail = "Item not found")

        product.image = product.image.strip("[]").split(",")
        
        return product
    except Exception as e:
        print("Error when get product: ", e)


# @router.get("/api/index/get_avg_price")
# def get_product(
#     by: str = Query(None, max_length=50),
#     name: str = Query(None, max_length=50),
#     product_id: str = Query(None, max_length=50)
#     ):
#     try:
#         db = SessionLocal()
#         if not by or (not name and not product_id):
#             raise HTTPException(status_code=404, detail="filter null")       
#         if product_id:
#             city_name = db.query(Property.location_city).filter(Property.id == product_id).scalar()
#             if by == "ward":
#                 name = db.query(Property.location_ward).filter(Property.id == product_id).scalar()
#                 average_price = db.query(func.avg(Property.price)).filter(Property.location_city == city_name).filter(Property.location_ward == name).scalar()
#             if by == "dist":
#                 name = db.query(Property.location_dist).filter(Property.id == product_id).scalar()
#                 average_price = db.query(func.avg(Property.price)).filter(Property.location_city == city_name).filter(Property.location_dist == name).scalar()
#         else:
#             if by == "ward":
#                 query = db.query(func.avg(Property.price))
#                 average_price = query.filter(Property.location_ward == name).scalar()
#             if by == "dist":  
#                 query = db.query(func.avg(Property.price))
#                 average_price = query.filter(Property.location_dist == name).scalar()
#         data = {
#             "by":by,
#             "name":name,
#             "value":average_price
#         }
        
#         return data
#     except Exception as e:
#         print("Error when get products: ",e)

@router.get("/api/index/get_avg_price")
def get_product(
    by: str = Query("dist", max_length=50),
    dist: str = Query(None, max_length=50),
    ward: str = Query(None, max_length=50),
    product_id: str = Query(None, max_length=50)
    ):
    try:
        db = SessionLocal()
        if not dist and not product_id:
            raise HTTPException(status_code=404, detail="filter null")       
        if product_id:
            if by == "ward":
                dist = db.query(Property.location_dist).filter(Property.id == product_id).scalar()
                ward = db.query(Property.location_ward).filter(Property.id == product_id).scalar()
                query = db.query(PriceAVG.avg_price)
                average_price = query.filter(PriceAVG.dist == dist).filter(PriceAVG.ward == ward).scalar()
            else:
                dist = db.query(Property.location_dist).filter(Property.id == product_id).scalar()
                query = db.query(func.sum(PriceAVG.avg_price * PriceAVG.num_item))
                data = query.filter(PriceAVG.dist == dist).scalar()
                num_item = db.query(func.sum(PriceAVG.num_item)).filter(PriceAVG.dist == dist).scalar()
                average_price = data / num_item
        else:
            if by == "ward":
                query = db.query(PriceAVG.avg_price)
                average_price = query.filter(PriceAVG.dist == dist).filter(PriceAVG.ward == ward).scalar()
            else:
                query = db.query(func.sum(PriceAVG.avg_price * PriceAVG.num_item))
                data = query.filter(PriceAVG.dist == dist).scalar()
                num_item = db.query(func.sum(PriceAVG.num_item)).filter(PriceAVG.dist == dist).scalar()
                average_price = data / num_item
                    

        data = {
            "by":by,
            "dist":dist,
            "ward":ward,
            "value":average_price
        }
        
        return data
    except Exception as e:
        print("Error when get products: ",e)

        
@router.get("/api/map/get_item_in_rec")
def get_product(
    lat_tl: float = Query(None),
    long_tl: float = Query(None),  
    lat_br: float = Query(None),
    long_br: float = Query(None),
    ):
    try:
        temp1 =min(lat_tl,lat_br)
        temp2 =min(long_tl,long_br)
        temp3 =max(lat_tl,lat_br)
        temp4 =max(long_tl,long_br)
        limit = 24
        db = SessionLocal()
        query = db.query(Property)
        query = query.filter(Property.location_lat >= temp1).filter(Property.location_lat <= temp3)
        query = query.filter(Property.location_long >= temp2).filter(Property.location_long <= temp4)
        
        query = query.limit(limit)
        data = query.all()
        
        if not data:
            raise HTTPException(status_code=404, detail="Not found")
        return data
    
    except Exception as e:
        print("Error when get products: ",e)


from . import models, schemas
from sqlalchemy.orm import Session

def get_products(db: Session, products_filters: schemas.ProductFilters):
    query = db.query(models.Products)

    if products_filters.category:
        query = query.filter(models.Products.property_type == products_filters.category)
    if products_filters.dist:
        query = query.filter(models.Products.location_dist == products_filters.dist)
    if products_filters.city:
        query = query.filter(models.Products.location_city == products_filters.city)
    if products_filters.q:
        query = query.filter(models.Products.title.like(f"%{products_filters.q}%"))
    if products_filters.lowest_price:
        query = query.filter(models.Products.price >= products_filters.lowest_price)
    if products_filters.highest_price:
        query = query.filter(models.Products.price <= products_filters.highest_price)
    if products_filters.lat_tl and products_filters.lat_br and products_filters.long_tl and products_filters.long_br:
        query = query.filter(models.Products.location_lat >= products_filters.lat_br).filter(models.Products.location_lat <= products_filters.lat_tl)
        query = query.filter(models.Products.location_long >= products_filters.long_tl).filter(models.Products.location_long <= products_filters.long_br)

    query = query.offset(products_filters.offset).limit(products_filters.limit)
    
    return query.all()
    
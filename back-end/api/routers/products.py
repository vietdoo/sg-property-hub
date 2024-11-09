from . import router, SessionLocal
from fastapi import Query, HTTPException
from ..domain.products import service, schemas

@router.get("/api/products")
def get_products(product_filters : schemas.ProductFilters):
    return service.get_products(db = SessionLocal(), products_filters = product_filters)


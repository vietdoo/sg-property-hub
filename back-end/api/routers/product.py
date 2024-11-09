from . import router, SessionLocal
from fastapi import Query, HTTPException
from ..domain.product import service, schemas

@router.get("/api/product")
def get_products(product_filter : schemas.ProductFilter):
    return service.get_product(db = SessionLocal(), products_filter = product_filter)


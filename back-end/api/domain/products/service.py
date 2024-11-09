
from . import schemas, repository

def get_products(db, products_filters: schemas.ProductFilters):
    return repository.get_products(db, products_filters)
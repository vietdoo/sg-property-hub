
from . import schemas, repository

def get_product(db, product_filter: schemas.ProductFilter):
    return repository.get_product(db, product_filter)
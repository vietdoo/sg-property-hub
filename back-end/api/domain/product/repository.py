from . import models, schemas
from sqlalchemy.orm import Session

def get_product(db: Session, product_filter: schemas.ProductFilter):
    return db.query(models.Products).filter(models.Products.id == product_filter.id).first()
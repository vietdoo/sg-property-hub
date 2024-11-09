from sqlalchemy.orm import declarative_base
from sqlalchemy import String, Text, Boolean, Integer, Column, BigInteger, ARRAY,Float

Base=declarative_base()


    
class PriceAVG(Base):
    __tablename__ = 'price_average'
    id = Column(Integer, primary_key=True, autoincrement=True)
    dist = Column(String(100))
    ward = Column(String(100))
    avg_price = Column(Float)
    num_item = Column(Integer)

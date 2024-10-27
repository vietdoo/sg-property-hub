from sqlalchemy.orm import declarative_base
from sqlalchemy import String, Text, Boolean, Integer, Column, BigInteger, ARRAY,Float

Base=declarative_base()
class House(Base):
    __tablename__ = 'house'
    url = Column(String)
    description = Column(Text)
    id = Column(String, primary_key=True)
    initial_at = Column(String)
    price = Column(BigInteger)
    price_currency = Column(String)
    price_string = Column(String)
    property_type = Column(String)
    publish_at = Column(String)
    site = Column(String)
    thumbnail = Column(String)
    title = Column(String)
    update_at = Column(String)
    initial_date = Column(String)
    images = Column(ARRAY(Text))
    
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
class Location(Base):
    __tablename__ = 'location'
    id = Column(String, primary_key=True)
    address = Column(String)
    city = Column(String)
    description = Column(String)
    dist = Column(String)
    lat = Column(Float)
    long = Column(Float)
    street = Column(String)
    ward = Column(String)
    
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
class Attr(Base):
    __tablename__ = 'attr'
    id = Column(String, primary_key=True)
    area = Column(Float)
    bathroom = Column(Integer)
    bedroom = Column(Integer)
    built_year = Column(Integer)
    certificate = Column(String)
    condition = Column(String)
    direction = Column(String)
    feature = Column(String)
    floor = Column(Float)
    floor_num = Column(Float)
    height = Column(Float)
    interior = Column(String)
    length = Column(Float)
    site_id = Column(String)
    total_area = Column(Float)
    total_room = Column(Integer)
    type_detail = Column(String)
    width = Column(Float)
    
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
class Agent(Base):
    __tablename__ = 'agent'
    id = Column(String, primary_key=True)
    address = Column(String)
    agent_type = Column(String)
    email = Column(String)
    name = Column(String)
    phone_number = Column(String)
    profile = Column(String)
    
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
class Project(Base):
    __tablename__ = 'project'
    id = Column(String, primary_key=True)
    name = Column(String)
    profile = Column(String)
    
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
class Property(Base):
    __tablename__ = 'property'
    url = Column(String)
    description = Column(Text)
    id = Column(String, primary_key=True)
    initial_at = Column(String)
    price = Column(BigInteger)
    price_currency = Column(String)
    price_string = Column(String)
    property_type = Column(String)
    publish_at = Column(String)
    site = Column(String)
    thumbnail = Column(String)
    title = Column(String)
    update_at = Column(String)
    initial_date = Column(String)
    agent_address = Column(String)
    agent_agent_type = Column(String)
    agent_email = Column(String)
    agent_name = Column(String)
    agent_phone_number = Column(String)
    agent_profile = Column(String)
    attr_area = Column(Float)
    attr_bathroom = Column(Integer)
    attr_bedroom = Column(Integer)
    attr_built_year = Column(Integer)
    attr_certificate = Column(String)
    attr_condition = Column(String)
    attr_direction = Column(String)
    attr_feature = Column(String)
    attr_floor = Column(Float)
    attr_floor_num = Column(Float)
    attr_height = Column(Float)
    attr_interior = Column(String)
    attr_length = Column(Float)
    attr_site_id = Column(String)
    attr_total_area = Column(Float)
    attr_total_room = Column(Integer)
    attr_type_detail = Column(String)
    attr_width = Column(Float)
    location_address = Column(String)
    location_city = Column(String)
    location_description = Column(String)
    location_dist = Column(String)
    location_lat = Column(Float)
    location_long = Column(Float)
    location_street = Column(String)
    location_ward = Column(String)
    project_name = Column(String)
    project_profile = Column(String)
    image = Column(Text)
    
class PriceAVG(Base):
    __tablename__ = 'price_average'
    id = Column(Integer, primary_key=True, autoincrement=True)
    dist = Column(String(100))
    ward = Column(String(100))
    avg_price = Column(Float)
    num_item = Column(Integer)

import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

POSTGRE_URL = os.environ.get('POSTGRE_URL')
engine = create_engine(POSTGRE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
import os
from fastapi import FastAPI
from sqlalchemy import create_engine, func, not_
from sqlalchemy.orm import sessionmaker, declarative_base
from .src.database import engine, SessionLocal, Base
from .routers import router as machine_router

app = FastAPI()
app.include_router(machine_router)
import os
from fastapi import FastAPI
from sqlalchemy import create_engine, func, not_
from sqlalchemy.orm import sessionmaker, declarative_base


POSTGRE_URL = os.environ.get('POSTGRE_URL')
engine = create_engine(POSTGRE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


from .routers import router as machine_router

app = FastAPI()
app.include_router(machine_router)

@app.get("/")
def root():
    """
    Returns a greeting message indicating that the API is up and running.

    Returns:
        dict: A dictionary containing a greeting message.
    """
    return {
        "message": "Welcome to the SGP Hub API. It is currently running and ready to serve requests.",
        "version": "1.0.3"
    }

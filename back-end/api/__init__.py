from fastapi import APIRouter

router = APIRouter()

from .routers import products_

router.include_router(products_.router)
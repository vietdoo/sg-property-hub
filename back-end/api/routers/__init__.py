from fastapi import APIRouter

router = APIRouter(tags=["stacks"])

from ..main import SessionLocal
from .products import *
from .product import *

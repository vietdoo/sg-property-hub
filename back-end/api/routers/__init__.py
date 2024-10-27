from fastapi import APIRouter

router = APIRouter(tags=["stacks"])

from ..main import SessionLocal, func, not_

from ..model import House, Location, Attr, Agent, Project, Property, PriceAVG

from .products import *

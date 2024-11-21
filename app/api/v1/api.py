from fastapi import APIRouter
from .endpoints.market_review import router as market_review_router

api_router = APIRouter()

api_router.include_router(
    market_review_router,
    prefix="/market-review",
    tags=["market-review"]
)
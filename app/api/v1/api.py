from fastapi import APIRouter
from .endpoints.market_review import router as market_review_router
from .endpoints.technical import router as technical_router
from .endpoints.stock import router as stock_router
from .endpoints.volume_price import router as volume_price_router
from app.market_view.router import router as market_view_router

api_router = APIRouter()

api_router.include_router(
    market_review_router,
    prefix="/market-review",
    tags=["market-review"]
)
api_router.include_router(
    technical_router,
    prefix="/technical",
    tags=["technical"]
)
api_router.include_router(
    stock_router,
    prefix="/stock",
    tags=["stock"]
)
api_router.include_router(
    volume_price_router,
    prefix="/volume-price",
    tags=["volume-price"]
)
api_router.include_router(
    market_view_router,
    prefix="/market",
    tags=["market"]
)
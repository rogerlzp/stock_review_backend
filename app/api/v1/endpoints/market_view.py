from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.market_view.service import MarketReviewService
from app.market_view.schemas import (
    MarketOverview, 
    SectorFlow, 
    TopList, 
    ConceptTheme,
    LimitUpStock, 
    TechnicalIndicator,
    DailyReview
)

router = APIRouter()

@router.get("/market-overview/{trade_date}", response_model=List[MarketOverview])
async def get_market_overview(trade_date: str):
    """获取市场概览"""
    try:
        data = await MarketReviewService.get_market_overview(trade_date)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sector-flow/{trade_date}", response_model=List[SectorFlow])
async def get_sector_flow(trade_date: str):
    """获取板块资金流向"""
    try:
        data = await MarketReviewService.get_sector_flow(trade_date)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/top-list/{trade_date}", response_model=List[TopList])
async def get_top_list(trade_date: str):
    """获取龙虎榜数据"""
    try:
        data = await MarketReviewService.get_top_list(trade_date)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/concepts/{trade_date}", response_model=List[ConceptTheme])
async def get_concepts(trade_date: str):
    """获取概念题材数据"""
    try:
        data = await MarketReviewService.get_concepts(trade_date)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/limit-up/{trade_date}", response_model=List[LimitUpStock])
async def get_limit_up(trade_date: str):
    """获取涨停板数据"""
    try:
        data = await MarketReviewService.get_limit_up(trade_date)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/technical/{trade_date}", response_model=List[TechnicalIndicator])
async def get_technical(trade_date: str):
    """获取技术指标数据"""
    try:
        data = await MarketReviewService.get_technical(trade_date)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/daily-review/{trade_date}", response_model=DailyReview)
async def get_daily_review(trade_date: str):
    """获取完整的每日复盘报告"""
    try:
        data = await MarketReviewService.get_daily_review(trade_date)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
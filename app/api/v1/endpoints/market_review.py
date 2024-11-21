from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.core.cache import RedisCache, get_cache
from app.core.validators import DateValidator
from app.database import get_db
from app.market_view.service import MarketReviewService
from loguru import logger

router = APIRouter()

def format_trade_date(date_str: str) -> str:
    """格式化交易日期，去掉日期中的横线"""
    return date_str.replace('-', '')

@router.get("/market-overview/{trade_date}")
async def get_market_overview(
    trade_date: str,
    db: Session = Depends(get_db),
    cache: RedisCache = Depends(get_cache)
):
    logger.info("Getting market overview for date: {}", trade_date)
    try:
        formatted_date = format_trade_date(trade_date)
        logger.debug("Formatted date: {}", formatted_date)
        service = MarketReviewService()
        market_data = await service.get_market_overview(formatted_date)
        return {"data": market_data}
    except Exception as e:
        logger.error("Error in get_market_overview: {}", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sector-flow/{trade_date}")
async def get_sector_flow(
    trade_date: str,
    db: Session = Depends(get_db),
    cache: RedisCache = Depends(get_cache)
):
    logger.info("Getting sector flow for date: {}", trade_date)
    try:
        formatted_date = format_trade_date(trade_date)
        logger.debug("Formatted date: {}", formatted_date)
        service = MarketReviewService()
        sector_data = await service.get_sector_flow(formatted_date)
        return {"data": sector_data}
    except Exception as e:
        logger.error("Error in get_sector_flow: {}", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/top-list/{trade_date}")
async def get_top_list(trade_date: str, db: Session = Depends(get_db)):
    logger.info("Getting top list for date: {}", trade_date)
    try:
        formatted_date = format_trade_date(trade_date)
        logger.debug("Formatted date: {}", formatted_date)
        service = MarketReviewService()
        top_list = await service.get_top_list(formatted_date)
        return {"data": top_list}
    except Exception as e:
        logger.error("Error in get_top_list: {}", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/concepts/{trade_date}")
async def get_concepts(trade_date: str, db: Session = Depends(get_db)):
    """获取概念列表"""
    logger.info("Getting concepts for date: {}", trade_date)
    try:
        formatted_date = format_trade_date(trade_date)
        logger.debug("Formatted date: {}", formatted_date)
        
        service = MarketReviewService()
        concepts = await service.get_concepts(formatted_date)
        
        if not concepts:
            logger.warning("No concept data found for date: {}", formatted_date)
            return {"data": []}
            
        return {"data": concepts}
        
    except Exception as e:
        logger.error("Error in get_concepts: {}", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/concept-stocks/{trade_date}/{concept_code}")
async def get_concept_stocks(
    trade_date: str,
    concept_code: str,
    db: Session = Depends(get_db)
):
    """获取概念成分股列表"""
    logger.info("Getting concept stocks for date: {} concept: {}", trade_date, concept_code)
    try:
        formatted_date = format_trade_date(trade_date)
        logger.debug("Formatted date: {}", formatted_date)
        
        service = MarketReviewService()
        stocks = await service.get_concept_stocks(formatted_date, concept_code)
        
        if not stocks:
            logger.warning("No stocks found for concept: {} on date: {}", concept_code, formatted_date)
            return {"data": []}
            
        return {"data": stocks}
        
    except Exception as e:
        logger.error("Error in get_concept_stocks: {}", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/limit-up-stocks/{trade_date}")
async def get_limit_up_stocks(trade_date: str, db: Session = Depends(get_db)):
    logger.info("Getting limit up stocks for date: {}", trade_date)
    try:
        formatted_date = format_trade_date(trade_date)
        logger.debug("Formatted date: {}", formatted_date)
        service = MarketReviewService()
        limit_up_data = await service.get_limit_up(formatted_date)
        return {"data": limit_up_data}
    except Exception as e:
        logger.error("Error in get_limit_up_stocks: {}", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) 
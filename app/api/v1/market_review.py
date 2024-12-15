from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from app.core.database import get_db
from app.market_view.market_review_service import MarketReviewService

router = APIRouter()

@router.get("/limit-analysis/{trade_date}")
def get_limit_analysis(
    trade_date: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """获取指定交易日的涨停板分析数据
    
    Args:
        trade_date: 交易日期，格式：YYYYMMDD
        
    Returns:
        Dict包含以下数据：
        - limit_stats: 涨停板统计（首板、二板等数量）
        - industry_distribution: 行业涨停分布
        - strongest_stocks: 最强涨停股（按封单金额）
        - fastest_stocks: 最快涨停股
        - last_stocks: 尾盘涨停股
        - broken_stocks: 炸板股统计
    """
    try:
        service = MarketReviewService(db)
        return service._get_limit_up_analysis(trade_date)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/daily-review/{trade_date}")
def get_daily_review(
    trade_date: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """获取指定交易日的市场复盘数据
    
    Args:
        trade_date: 交易日期，格式：YYYYMMDD
        
    Returns:
        Dict包含以下数据：
        - hot_sectors: 热门板块
        - capital_flow: 资金流向
        - market_stats: 市场统计
        - limit_up_analysis: 涨停分析
        - concept_analysis: 概念分析
    """
    try:
        service = MarketReviewService(db)
        return service.get_daily_review(trade_date)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/market/stock/{ts_code}")
async def get_stock_detail(
    ts_code: str,
    trade_date: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """获取股票详细信息
    
    Args:
        ts_code: 股票代码
        trade_date: 交易日期，格式：YYYYMMDD
        
    Returns:
        Dict包含股票的详细信息，包括：
        - 基本信息（代码、名称等）
        - 交易数据（开盘价、最高价、最低价等）
        - 涨停信息（涨停时间、原因等）
    """
    try:
        service = MarketReviewService(db)
        return await service.get_stock_detail(ts_code, trade_date)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/market/stock/{ts_code}/limit-history")
async def get_limit_history(
    ts_code: str,
    trade_date: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """获取股票的连板历史数据"""
    try:
        service = MarketReviewService(db)
        return await service.get_limit_history(ts_code, trade_date)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/market/stock/{ts_code}/volume-analysis")
async def get_volume_analysis(
    ts_code: str,
    trade_date: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """获取股票的30日成交量分析数据"""
    try:
        service = MarketReviewService(db)
        return await service.get_volume_analysis(ts_code, trade_date)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

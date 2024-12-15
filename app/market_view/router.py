from fastapi import APIRouter, Query, Body, HTTPException, Depends
from typing import Optional, List, Dict, Any
from .service import MarketReviewService
from .stock_compare_service import StockCompareService
from pydantic import BaseModel
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.core.database import get_db

router = APIRouter()

class StockCompareRequest(BaseModel):
    ts_code1: str
    ts_code2: str
    start_date: str
    end_date: str

@router.get("/overview")
async def get_market_overview(trade_date: str = Query(..., description="交易日期，格式：YYYYMMDD")):
    return await MarketReviewService.get_market_overview(trade_date)

@router.get("/sector-flow")
async def get_sector_flow(trade_date: str = Query(..., description="交易日期，格式：YYYYMMDD")):
    return await MarketReviewService.get_sector_flow(trade_date)

@router.get("/top-list")
async def get_top_list(trade_date: str = Query(..., description="交易日期，格式：YYYYMMDD")):
    return await MarketReviewService.get_top_list(trade_date)

@router.get("/limit-up")
async def get_limit_up(
    trade_date: str = Query(..., description="交易日期，格式：YYYYMMDD"),
    limit_times: Optional[int] = Query(None, description="连板数"),
    up_stat: Optional[str] = Query(None, description="涨停统计")
):
    return await MarketReviewService.get_limit_up(trade_date, limit_times, up_stat)

@router.get("/technical")
async def get_technical(trade_date: str = Query(..., description="交易日期，格式：YYYYMMDD")):
    return await MarketReviewService.get_technical(trade_date)

@router.get("/concepts")
async def get_concepts(trade_date: str = Query(..., description="交易日期，格式：YYYYMMDD")):
    return await MarketReviewService.get_concepts(trade_date)

@router.get("/daily-review")
async def get_daily_review(trade_date: str = Query(..., description="交易日期，格式：YYYYMMDD")):
    return await MarketReviewService.get_daily_review(trade_date)

@router.get("/stock/detail/{ts_code}")
async def get_stock_detail(
    ts_code: str,
    trade_date: str = Query(..., description="交易日期，格式：YYYYMMDD")
):
    return await MarketReviewService.get_stock_detail(ts_code, trade_date)

@router.get("/stock/limit-history/{ts_code}")
async def get_limit_history(
    ts_code: str,
    trade_date: str = Query(..., description="交易日期，格式：YYYYMMDD")
):
    return await MarketReviewService.get_limit_history(ts_code, trade_date)

@router.get("/stock/volume-analysis/{ts_code}")
async def get_volume_analysis(
    ts_code: str,
    trade_date: str = Query(..., description="交易日期，格式：YYYYMMDD")
):
    return await MarketReviewService.get_volume_analysis(ts_code, trade_date)

@router.get("/stock/weekly-analysis")
def get_weekly_analysis(
    ts_code: str,
    start_date: str = Query(default=None),
    end_date: str = Query(default=None)
):
    """
    获取股票的周度分析数据，包括：
    - 每周涨跌分布
    - 不同星期几的涨跌特征
    - 成交量和换手率的周内分布
    - 资金流向的周内特征
    """
    if not start_date:
        # 默认查询最近3个月的数据
        end_date = datetime.now().strftime("%Y%m%d")
        start_date = (datetime.now() - timedelta(days=90)).strftime("%Y%m%d")
    elif not end_date:
        end_date = datetime.now().strftime("%Y%m%d")
        
    return StockCompareService.get_weekly_analysis(ts_code, start_date, end_date)

@router.get("/stock/weekly-pattern/{ts_code}")
def get_stock_weekly_pattern(
    ts_code: str,
    start_date: str = Query(None, description="开始日期，格式：YYYYMMDD"),
    end_date: str = Query(None, description="结束日期，格式：YYYYMMDD"),
    db: Session = Depends(get_db)
):
    """获取股票周度交易规律分析
    
    Args:
        ts_code: 股票代码
        start_date: 开始日期 (可选，格式：YYYYMMDD)
        end_date: 结束日期 (可选，格式：YYYYMMDD)
    """
    service = StockCompareService(db)
    return service.get_weekly_pattern(ts_code, start_date, end_date)

@router.post("/stock/compare")
def compare_stocks(
    request: StockCompareRequest = Body(..., description="股票比较请求参数")
):
    """比较两只股票的量价走势"""
    return StockCompareService.get_stock_comparison(
        request.ts_code1,
        [request.ts_code2] if request.ts_code2 != request.ts_code1 else [],
        request.start_date,
        request.end_date
    )

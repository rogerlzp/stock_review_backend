from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.core.database import get_db
from app.market_view.volume_price_service import StockVolumePriceService
from app.market_view.market_volume_price_service import MarketVolumePriceService
from loguru import logger

logger = logger.bind(module=__name__)

router = APIRouter(prefix="/volume-price")

def validate_date(date_str: str) -> str:
    """验证日期格式并返回标准格式 (YYYY-MM-DD)"""
    try:
        # 尝试解析日期
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime("%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail="Invalid date format. Please use YYYY-MM-DD format."
        )

@router.get("/stock")
def get_stock_volume_price(
    ts_codes: List[str] = Query(..., description="股票代码列表"),
    trade_date: str = Query(..., description="交易日期，格式：YYYY-MM-DD"),
    db: Session = Depends(get_db)
):
    """获取指定股票的量价分析"""
    logger.info("Getting stock volume price for stocks: {}, date: {}", ts_codes, trade_date)
    try:
        trade_date = validate_date(trade_date)
        service = StockVolumePriceService(db)
        return service.get_stock_volume_price_analysis(ts_codes, trade_date)
    except Exception as e:
        logger.error("Error in get_stock_volume_price: {}", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/market")
def get_market_volume_price_anomalies(
    trade_date: str = Query(..., description="交易日期，格式：YYYY-MM-DD"),
    anomaly_types: Optional[List[str]] = Query(None, description="异常类型列表"),
    limit: int = Query(50, ge=1, le=200, description="返回记录数"),
    sort_by: str = Query("anomaly_score", description="排序字段"),
    db: Session = Depends(get_db)
):
    """获取市场量价异常股票列表"""
    logger.info("Getting market volume price anomalies for date: {}", trade_date)
    try:
        trade_date = validate_date(trade_date)
        service = MarketVolumePriceService(db)
        return service.get_market_volume_price_anomalies(trade_date, anomaly_types, limit, sort_by)
    except Exception as e:
        logger.error("Error in get_market_volume_price_anomalies: {}", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stock/info")
def get_stock_info(
    code: str = Query(..., description="股票代码"),
    trade_date: str = Query(..., description="交易日期，格式：YYYY-MM-DD"),
    db: Session = Depends(get_db)
):
    """获取股票基本信息"""
    logger.info("Getting stock info for code: {}, date: {}", code, trade_date)
    try:
        trade_date = validate_date(trade_date)
        service = StockVolumePriceService(db)
        return service.get_stock_info(code, trade_date)
    except Exception as e:
        logger.error("Error in get_stock_info: {}", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stock/volume-price")
def get_stock_volume_price_data(
    code: str = Query(..., description="股票代码"),
    trade_date: str = Query(..., description="交易日期，格式：YYYY-MM-DD"),
    db: Session = Depends(get_db)
):
    """获取个股量价数据"""
    logger.info("Getting stock volume price data for code: {}, date: {}", code, trade_date)
    try:
        trade_date = validate_date(trade_date)
        service = StockVolumePriceService(db)
        return service.get_stock_volume_price(code, trade_date)
    except Exception as e:
        logger.error("Error in get_stock_volume_price_data: {}", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/market/volume")
def get_market_volume_data(
    trade_date: str = Query(..., description="交易日期，格式：YYYY-MM-DD"),
    db: Session = Depends(get_db)
):
    """获取市场量价数据"""
    logger.info("Getting market volume data for date: {}", trade_date)
    try:
        trade_date = validate_date(trade_date)
        service = MarketVolumePriceService(db)
        return service.get_market_volume_data(trade_date)
    except Exception as e:
        logger.error("Error in get_market_volume_data: {}", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/market/anomaly")
def get_anomaly_stocks(
    trade_date: str = Query(..., description="交易日期，格式：YYYY-MM-DD"),
    type: str = Query(..., description="异常类型"),
    db: Session = Depends(get_db)
):
    """获取异常股票列表"""
    logger.info("Getting anomaly stocks for date: {}, type: {}", trade_date, type)
    try:
        trade_date = validate_date(trade_date)
        valid_types = {'volume_up', 'volume_down', 'volume_decrease_up', 'volume_decrease_down'}
        if type not in valid_types:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid type. Must be one of: {', '.join(valid_types)}"
            )
        
        service = MarketVolumePriceService(db)
        return service.get_anomaly_stocks(trade_date, type)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error in get_anomaly_stocks: {}", str(e))
        raise HTTPException(status_code=500, detail=str(e))

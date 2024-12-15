from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List
from app.market_view.technical_service import TechnicalAnalysisService
from loguru import logger
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/indicators")
async def get_technical_indicators(
    ts_code: str = Query(..., description="股票代码"),
    end_date: str = Query(None, description="结束日期，格式：YYYYMMDD，默认为最新交易日"),
    period: int = Query(90, description="获取天数，默认90天")
) -> Dict[str, Any]:
    """获取股票技术指标分析，默认获取最近3个月数据"""
    try:
        result = await TechnicalAnalysisService.get_technical_indicators(
            ts_code=ts_code,
            end_date=end_date,
            period=period
        )
        return {
            "code": 0,
            "message": "success",
            "data": result
        }
    except Exception as e:
        logger.error(f"Error in get_technical_indicators: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any
from app.market_view.technical_service import TechnicalAnalysisService
from loguru import logger

router = APIRouter()

@router.get("/indicators")
async def get_technical_indicators(
    ts_code: str = Query(..., description="股票代码"),
    trade_date: str = Query(..., description="交易日期，格式：YYYYMMDD")
) -> Dict[str, Any]:
    """获取股票技术指标分析"""
    try:
        result = await TechnicalAnalysisService.get_technical_indicators(ts_code, trade_date)
        return {
            "code": 0,
            "message": "success",
            "data": result
        }
    except Exception as e:
        logger.error(f"Error in get_technical_indicators: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

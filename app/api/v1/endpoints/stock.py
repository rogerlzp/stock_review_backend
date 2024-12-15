from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from app.models.stock import StockBasic
from app.models.limit_list import LimitList
from app.core.database import get_db
from app.schemas.stock import StockBasicResponse, LimitListResponse, StockDetailResponse
from sqlalchemy import or_, text

router = APIRouter()

@router.get("/search", response_model=List[StockBasicResponse])
async def search_stocks(query: str, db: Session = Depends(get_db)):
    """
    搜索股票，支持按代码或名称搜索
    """
    if not query:
        return []
    
    stocks = db.query(StockBasic).filter(
        or_(
            StockBasic.ts_code.ilike(f"%{query}%"),
            StockBasic.symbol.ilike(f"%{query}%"),
            StockBasic.name.ilike(f"%{query}%")
        )
    ).limit(10).all()
    
    return stocks

@router.get("/detail", response_model=StockDetailResponse)
async def get_stock_detail(
    ts_code: str,
    start_date: str,
    end_date: str,
    db: Session = Depends(get_db)
):
    """获取股票详细信息，包括日线数据和技术指标"""
    # 1. 获取股票基本信息
    stock_info = db.query(StockBasic).filter(StockBasic.ts_code == ts_code).first()
    if not stock_info:
        raise HTTPException(status_code=404, detail="Stock not found")

    # 2. 获取日线数据
    daily_query = text("""
        SELECT 
            trade_date,
            open,
            high,
            low,
            close,
            pre_close,
            vol as volume,
            amount,
            pct_chg,
            turnover_rate
        FROM stock_daily
        WHERE ts_code = :ts_code 
        AND trade_date BETWEEN :start_date AND :end_date
        ORDER BY trade_date ASC
    """)
    daily_result = db.execute(
        daily_query,
        {
            "ts_code": ts_code,
            "start_date": start_date,
            "end_date": end_date
        }
    )
    daily_data = [dict(row) for row in daily_result]

    # 3. 获取技术指标数据
    tech_query = text("""
        SELECT 
            trade_date,
            ma5,
            ma10,
            ma20,
            ma60,
            vol_ma5,
            vol_ma10,
            vol_ma20,
            macd_dif,
            macd_dea,
            macd,
            kdj_k,
            kdj_d,
            kdj_j,
            rsi_6,
            rsi_12,
            rsi_24
        FROM stock_technical
        WHERE ts_code = :ts_code 
        AND trade_date BETWEEN :start_date AND :end_date
        ORDER BY trade_date ASC
    """)
    tech_result = db.execute(
        tech_query,
        {
            "ts_code": ts_code,
            "start_date": start_date,
            "end_date": end_date
        }
    )
    technical_data = [dict(row) for row in tech_result]

    # 4. 获取涨跌停数据
    limit_query = text("""
        SELECT 
            trade_date,
            lu_time,
            ld_time,
            status
        FROM kpl_list
        WHERE ts_code = :ts_code 
        AND trade_date BETWEEN :start_date AND :end_date
        ORDER BY trade_date ASC
    """)
    limit_result = db.execute(
        limit_query,
        {
            "ts_code": ts_code,
            "start_date": start_date,
            "end_date": end_date
        }
    )
    limit_data = [dict(row) for row in limit_result]

    return {
        "basic": {
            "ts_code": stock_info.ts_code,
            "name": stock_info.name,
            "industry": stock_info.industry,
            "market": stock_info.market
        },
        "daily": daily_data,
        "technical": technical_data,
        "limit": limit_data
    }

@router.get("/limit_list", response_model=List[LimitListResponse])
async def get_limit_list(
    limit_times: Optional[int] = None,
    up_stat: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    获取符合连板次数和涨停统计的股票列表
    """
    stocks = LimitList.filter_by_criteria(db, limit_times, up_stat)
    return stocks

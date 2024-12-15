from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from app.models.stock import StockBasic
from app.models.limit_list import LimitList
from app.core.database import get_db
from app.schemas.stock import StockBasicResponse, LimitListResponse
from sqlalchemy import or_

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

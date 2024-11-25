from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List
from app.models.stock import StockBasic
from app.database import get_db
from app.schemas.stock import StockBasicResponse

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

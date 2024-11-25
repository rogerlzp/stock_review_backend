from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Dict
from . import models
from .models import StockConcept
import logging

logger = logging.getLogger(__name__)

def get_market_overview(db: Session, trade_date: str) -> Optional[models.MarketOverview]:
    return db.query(models.MarketOverview).filter(
        models.MarketOverview.trade_date == trade_date
    ).first()

def get_sector_fund_flows(db: Session, trade_date: str) -> List[models.SectorFlow]:
    return db.query(models.SectorFlow).filter(
        models.SectorFlow.trade_date == trade_date
    ).all()

def get_sector_stocks(db: Session, sector_id: int) -> List[models.SectorStock]:
    return db.query(models.SectorStock).filter(
        models.SectorStock.sector_id == sector_id
    ).all()

def get_top_list(db: Session, trade_date: str) -> List[models.TopList]:
    return db.query(models.TopList).filter(
        models.TopList.trade_date == trade_date
    ).all()

def get_top_buyers(db: Session, top_list_id: int) -> List[models.TopListTrader]:
    return db.query(models.TopListTrader).filter(
        models.TopListTrader.buy_list_id == top_list_id
    ).all()

def get_top_sellers(db: Session, top_list_id: int) -> List[models.TopListTrader]:
    return db.query(models.TopListTrader).filter(
        models.TopListTrader.sell_list_id == top_list_id
    ).all()

def get_concepts(db: Session, trade_date: str) -> List[models.Concept]:
    return db.query(models.Concept).filter(
        models.Concept.trade_date == trade_date
    ).all()

def get_concept_stocks(db: Session, date: str, code: str) -> List[Dict]:
    """获取概念成分股列表"""
    try:
        # 使用code查询概念成分股
        stocks = db.query(StockConcept).filter(
            StockConcept.trade_date == date,
            StockConcept.concept_code == code
        ).all()
        
        if not stocks:
            return []
            
        # 转换为字典列表
        return [
            {
                "code": stock.stock_code,
                "name": stock.stock_name,
                "price": stock.close_price,
                "pct_change": stock.pct_change,
                "turnover_rate": stock.turnover_rate,
                "volume": stock.volume,
                "amount": stock.amount
            }
            for stock in stocks
        ]
        
    except Exception as e:
        logger.error(f"获取概念成分股失败: {str(e)}")
        raise e

def get_concept_leading_stocks(db: Session, concept_id: int) -> List[models.ConceptStock]:
    return db.query(models.ConceptStock).filter(
        models.ConceptStock.concept_id == concept_id,
        models.ConceptStock.is_leading == 1
    ).all()

def get_limit_up_stocks(db: Session, trade_date: str) -> List[models.LimitUp]:
    return db.query(models.LimitUp).filter(
        models.LimitUp.trade_date == trade_date
    ).all()
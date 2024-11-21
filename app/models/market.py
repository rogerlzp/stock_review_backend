from sqlalchemy import Column, String, Float, Integer, Date
from app.database import Base

class IndexDailyBasic(Base):
    __tablename__ = 'index_dailybasic'

    id = Column(Integer, primary_key=True, index=True)
    ts_code = Column(String, index=True)
    trade_date = Column(String, index=True)
    total_mv = Column(Float)
    float_mv = Column(Float)
    total_share = Column(Float)
    float_share = Column(Float)
    free_share = Column(Float)
    turnover_rate = Column(Float)
    turnover_rate_f = Column(Float)
    pe = Column(Float)
    pe_ttm = Column(Float)
    pb = Column(Float)

class StockDaily(Base):
    __tablename__ = 'stock_daily'

    id = Column(Integer, primary_key=True, index=True)
    ts_code = Column(String, index=True)
    trade_date = Column(String, index=True)
    close = Column(Float)
    pct_chg = Column(Float)
    amount = Column(Float) 
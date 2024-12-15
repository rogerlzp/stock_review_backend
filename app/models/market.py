from sqlalchemy import Column, String, Float, Date, Integer
from app.core.database import Base

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

class GgtDaily(Base):
    """港股通每日成交"""
    __tablename__ = 'ggt_daily'

    id = Column(Integer, primary_key=True, index=True)
    trade_date = Column(Date, index=True)
    buy_amount = Column(Float, comment="买入成交金额（亿元）")
    buy_volume = Column(Float, comment="买入成交笔数（万笔）")
    sell_amount = Column(Float, comment="卖出成交金额（亿元）")
    sell_volume = Column(Float, comment="卖出成交笔数（万笔）")

class Margin(Base):
    """融资融券交易汇总"""
    __tablename__ = 'margin'

    id = Column(Integer, primary_key=True, index=True)
    trade_date = Column(Date, index=True)
    exchange_id = Column(String, index=True, comment="交易所代码")
    rzye = Column(Float, comment="融资余额(元)")
    rzmre = Column(Float, comment="融资买入额(元)")
    rzche = Column(Float, comment="融资偿还额(元)")
    rqye = Column(Float, comment="融券余额(元)")
    rqmcl = Column(Float, comment="融券卖出量(股,份,手)")
    rzrqye = Column(Float, comment="融资融券余额(元)")
    rqyl = Column(Float, comment="融券余量(股,份,手)")
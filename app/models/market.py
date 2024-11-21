from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class MarketOverview(Base):
    __tablename__ = "market_overview"

    id = Column(Integer, primary_key=True, index=True)
    trade_date = Column(String, index=True)
    index_value = Column(Float)
    index_change = Column(Float)
    total_amount = Column(Float)
    up_count = Column(Integer)
    down_count = Column(Integer)

class SectorFlow(Base):
    __tablename__ = "sector_flow"

    id = Column(Integer, primary_key=True, index=True)
    trade_date = Column(String, index=True)
    sector_name = Column(String, index=True)
    inflow = Column(Float)
    outflow = Column(Float)
    net_flow = Column(Float)
    stocks = relationship("SectorStock", back_populates="sector")

class SectorStock(Base):
    __tablename__ = "sector_stocks"

    id = Column(Integer, primary_key=True, index=True)
    sector_id = Column(Integer, ForeignKey("sector_flow.id"))
    stock_code = Column(String)
    stock_name = Column(String)
    sector = relationship("SectorFlow", back_populates="stocks")

class TopList(Base):
    __tablename__ = "top_list"

    id = Column(Integer, primary_key=True, index=True)
    trade_date = Column(String, index=True)
    stock_code = Column(String, index=True)
    stock_name = Column(String)
    price = Column(Float)
    change = Column(Float)
    amount = Column(Float)
    buyers = relationship("TopListTrader", foreign_keys="TopListTrader.buy_list_id")
    sellers = relationship("TopListTrader", foreign_keys="TopListTrader.sell_list_id")

class TopListTrader(Base):
    __tablename__ = "top_list_traders"

    id = Column(Integer, primary_key=True, index=True)
    buy_list_id = Column(Integer, ForeignKey("top_list.id"))
    sell_list_id = Column(Integer, ForeignKey("top_list.id"))
    trader_name = Column(String)
    amount = Column(Float)

class Concept(Base):
    __tablename__ = "concepts"

    id = Column(Integer, primary_key=True, index=True)
    trade_date = Column(String, index=True)
    name = Column(String, index=True)
    stock_count = Column(Integer)
    avg_change = Column(Float)
    description = Column(String)
    stocks = relationship("ConceptStock", back_populates="concept")

class ConceptStock(Base):
    __tablename__ = "concept_stocks"

    id = Column(Integer, primary_key=True, index=True)
    concept_id = Column(Integer, ForeignKey("concepts.id"))
    stock_code = Column(String)
    stock_name = Column(String)
    is_leading = Column(Integer, default=0)  # 0: 普通成分股, 1: 龙头股
    concept = relationship("Concept", back_populates="stocks")

class LimitUp(Base):
    __tablename__ = "limit_up"

    id = Column(Integer, primary_key=True, index=True)
    trade_date = Column(String, index=True)
    stock_code = Column(String, index=True)
    stock_name = Column(String)
    limit_up_time = Column(DateTime)
    reason = Column(String)
    turnover_rate = Column(Float)
    amount = Column(Float) 
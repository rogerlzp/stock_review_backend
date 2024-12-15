from sqlalchemy import Column, String, Float, Date, Integer, ForeignKey, DateTime, func
from app.core.database import Base
from sqlalchemy.orm import relationship

class StockBasic(Base):
    """股票基本信息"""
    __tablename__ = "stock_basic"
    
    id = Column(Integer, primary_key=True, index=True)
    ts_code = Column(String, unique=True, index=True, comment="TS代码")
    symbol = Column(String, comment="股票代码")
    name = Column(String, comment="股票名称")
    area = Column(String, comment="地域")
    industry = Column(String, comment="所属行业")
    fullname = Column(String, comment="股票全称")
    enname = Column(String, comment="英文全称")
    market = Column(String, comment="市场类型")
    exchange = Column(String, comment="交易所代码")
    curr_type = Column(String, comment="交易货币")
    list_status = Column(String, comment="上市状态")
    list_date = Column(Date, comment="上市日期")
    delist_date = Column(Date, comment="退市日期")
    is_hs = Column(String, comment="是否沪深港通标的")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    def __str__(self):
        return f"{self.ts_code} - {self.name}"

class StockDaily(Base):
    """股票日线数据"""
    __tablename__ = "stock_daily"

    id = Column(Integer, primary_key=True, index=True)
    ts_code = Column(String, index=True, comment="股票代码")
    trade_date = Column(Date, comment="交易日期")
    open = Column(Float, comment="开盘价")
    high = Column(Float, comment="最高价")
    low = Column(Float, comment="最低价")
    close = Column(Float, comment="收盘价")
    pre_close = Column(Float, comment="前收盘价")
    change = Column(Float, comment="涨跌额")
    pct_chg = Column(Float, comment="涨跌幅")
    vol = Column(Float, comment="成交量")
    amount = Column(Float, comment="成交额")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

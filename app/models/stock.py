from sqlalchemy import Column, Integer, String, Date, DateTime, func
from app.database import Base

class StockBasic(Base):
    """股票基本信息"""
    __tablename__ = "stock_basic"
    
    id = Column(Integer, primary_key=True, index=True)
    ts_code = Column(String(10), unique=True, index=True, nullable=False, comment="股票代码")
    symbol = Column(String(10), index=True, nullable=False, comment="股票代码（不含市场标识）")
    name = Column(String(100), index=True, nullable=False, comment="股票名称")
    area = Column(String(50), nullable=True, comment="地域")
    industry = Column(String(50), nullable=True, comment="所属行业")
    market = Column(String(50), nullable=False, comment="市场类型（主板/创业板/科创板/CDR）")
    list_date = Column(Date, nullable=True, comment="上市日期")
    is_hs = Column(String(1), nullable=True, comment="是否是沪深股票")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    def __str__(self):
        return f"{self.ts_code} - {self.name}"

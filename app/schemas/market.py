from pydantic import BaseModel
from typing import List

class MarketOverviewData(BaseModel):
    tradeDate: str
    shangzhengIndex: float
    shangzhengChange: float
    totalAmount: float
    upCount: int
    downCount: int

class SectorFlowData(BaseModel):
    sectorName: str
    inflow: float
    outflow: float
    netFlow: float
    stockList: List[str]

class TopListData(BaseModel):
    stockCode: str
    stockName: str
    price: float
    change: float
    amount: float
    buyList: List[str]
    sellList: List[str]

class ConceptData(BaseModel):
    conceptName: str
    stockCount: int
    avgChange: float
    leadingStocks: List[str]
    description: str

class LimitUpData(BaseModel):
    stockCode: str
    stockName: str
    limitUpTime: str
    limitUpReason: str
    turnoverRate: float
    amount: float 
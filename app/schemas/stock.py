from pydantic import BaseModel, validator
from datetime import date, datetime
from typing import Optional, List

class StockBasicResponse(BaseModel):
    ts_code: str
    symbol: str
    name: str
    area: Optional[str] = None
    industry: Optional[str] = None
    market: str
    list_date: Optional[str] = None
    is_hs: Optional[str] = None
    
    @validator('list_date')
    def validate_list_date(cls, v):
        if not v:
            return None
        try:
            return datetime.strptime(v, '%Y%m%d').date().isoformat()
        except (ValueError, TypeError):
            return None
    
    class Config:
        orm_mode = True


class LimitListResponse(BaseModel):
    trade_date: str
    ts_code: str
    industry: Optional[str] = None
    name: str
    close: float
    pct_chg: float
    amount: float
    limit_amount: Optional[float] = None
    float_mv: float
    total_mv: float
    turnover_ratio: float
    fd_amount: Optional[float] = None
    first_time: Optional[str] = None
    last_time: Optional[str] = None
    open_times: int
    up_stat: Optional[str] = None
    limit_times: int
    limit: str

    class Config:
        orm_mode = True


class StockBasicResponseNew(BaseModel):
    ts_code: str
    name: str
    industry: Optional[str] = None
    market: Optional[str] = None

class LimitListResponseNew(BaseModel):
    ts_code: str
    name: str
    limit_times: Optional[int] = None
    up_stat: Optional[str] = None

class DailyData(BaseModel):
    trade_date: str
    open: float
    high: float
    low: float
    close: float
    pre_close: float
    volume: float
    amount: float
    pct_chg: float
    turnover_rate: float

class TechnicalData(BaseModel):
    trade_date: str
    ma5: Optional[float] = None
    ma10: Optional[float] = None
    ma20: Optional[float] = None
    ma60: Optional[float] = None
    vol_ma5: Optional[float] = None
    vol_ma10: Optional[float] = None
    vol_ma20: Optional[float] = None
    macd_dif: Optional[float] = None
    macd_dea: Optional[float] = None
    macd: Optional[float] = None
    kdj_k: Optional[float] = None
    kdj_d: Optional[float] = None
    kdj_j: Optional[float] = None
    rsi_6: Optional[float] = None
    rsi_12: Optional[float] = None
    rsi_24: Optional[float] = None

class LimitData(BaseModel):
    trade_date: str
    lu_time: Optional[str] = None
    ld_time: Optional[str] = None
    status: Optional[str] = None

class StockDetailResponse(BaseModel):
    basic: StockBasicResponseNew
    daily: List[DailyData]
    technical: List[TechnicalData]
    limit: List[LimitData]

class StockCompareRequest(BaseModel):
    base_stock: str
    compare_stocks: List[str]
    start_date: str
    end_date: str

class CompareStockData(BaseModel):
    ts_code: str
    name: str
    industry: Optional[str] = None
    market: Optional[str] = None
    daily: List[DailyData]
    limit: List[LimitData]

class StockComparisonResponse(BaseModel):
    base_stock: CompareStockData
    compare_stocks: List[CompareStockData]

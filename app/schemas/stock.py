from pydantic import BaseModel, validator
from datetime import date, datetime
from typing import Optional

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

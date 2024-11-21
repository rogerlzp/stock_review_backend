from datetime import datetime
from typing import Optional
from pydantic import BaseModel, validator

class DateValidator(BaseModel):
    trade_date: str

    @validator('trade_date')
    def validate_trade_date(cls, v):
        try:
            # 验证日期格式
            datetime.strptime(v, '%Y-%m-%d')
            # 验证是否是交易日
            if not is_trading_day(v):
                raise ValueError("非交易日")
            return v
        except ValueError as e:
            raise ValueError(f"无效的交易日期: {str(e)}")

def is_trading_day(date_str: str) -> bool:
    """检查是否为交易日"""
    try:
        # 这里可以接入 tushare 或其他数据源来验证是否为交易日
        # 示例实现
        date = datetime.strptime(date_str, '%Y-%m-%d')
        # 周末不是交易日
        if date.weekday() > 4:
            return False
        # TODO: 检查节假日
        return True
    except:
        return False 
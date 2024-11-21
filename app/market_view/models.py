from datetime import date
from pydantic import BaseModel
from typing import List, Optional

class MarketOverview(BaseModel):
    """市场概览数据模型"""
    index_code: str
    index_name: str
    close: float
    change: float
    pct_chg: float
    vol: float
    amount: float
    turnover_rate: float

class SectorFlow(BaseModel):
    """板块资金流向数据模型"""
    sector_name: str
    pct_change: float
    net_amount: float
    net_amount_rate: float
    buy_elg_amount: float  # 超大单
    buy_lg_amount: float   # 大单
    buy_md_amount: float   # 中单
    buy_sm_amount: float   # 小单
    hot_stock: str         # 领涨股

class TopList(BaseModel):
    """龙虎榜数据模型"""
    ts_code: str
    name: str
    close: float
    pct_change: float
    turnover_rate: float
    l_buy: float
    l_sell: float
    net_amount: float
    reason: str
    exalter: Optional[str]     # 营业部名称
    buy: Optional[float]       # 买入额
    sell: Optional[float]      # 卖出额
    net_buy: Optional[float]   # 净买入

class ConceptTheme(BaseModel):
    """概念题材数据模型"""
    ts_code: str
    name: str
    z_t_num: int              # 涨停数量
    up_num: int               # 上升位数
    stock_count: int          # 成分股数量
    cons_list: List[str]      # 成分股列表
    hot_num: Optional[int]    # 人气值
    desc: Optional[str]       # 描述

class LimitUpStock(BaseModel):
    """涨停板数据模型"""
    ts_code: str
    name: str
    lu_time: str             # 涨停时间
    open_time: Optional[str]  # 开板时间
    last_time: Optional[str]  # 最后涨停时间
    lu_desc: str             # 涨停原因
    theme: str               # 所属板块
    net_change: float        # 主力净额
    status: str              # 连板状态
    turnover_rate: float     # 换手率
    lu_limit_order: float    # 封单量
    bid_amount: float        # 竞价金额
    bid_turnover: float      # 竞价换手
    amount: float            # 成交额
    free_float: float        # 实际流通

class TechnicalIndicator(BaseModel):
    """技术指标数据模型"""
    ts_code: str
    close: float
    # MACD指标
    macd_bfq: float
    macd_dea_bfq: float
    macd_dif_bfq: float
    # KDJ指标
    kdj_k_bfq: float
    kdj_d_bfq: float
    kdj_bfq: float
    # RSI指标
    rsi_bfq_6: float
    rsi_bfq_12: float
    rsi_bfq_24: float
    # BOLL指标
    boll_upper_bfq: float
    boll_mid_bfq: float
    boll_lower_bfq: float
    # 其他常用指标
    ma_bfq_5: float
    ma_bfq_10: float
    ma_bfq_20: float
    ma_bfq_60: float
    vol: float
    amount: float
    turnover_rate: float

class DailyReview(BaseModel):
    """每日复盘完整数据模型"""
    date: str
    market_overview: List[MarketOverview]
    sector_flow: List[SectorFlow]
    top_list: List[TopList]
    concepts: List[ConceptTheme]
    limit_up: List[LimitUpStock]
    technical: List[TechnicalIndicator]
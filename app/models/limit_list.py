from sqlalchemy import Column, String, Float, Integer, DateTime
from app.core.database import Base
from typing import Optional
from sqlalchemy.orm import Session

class LimitList(Base):
    """涨跌停数据表"""
    __tablename__ = 'limit_list'

    # 复合主键：交易日期 + 股票代码
    trade_date = Column(String(8), primary_key=True, comment='交易日期')
    ts_code = Column(String(10), primary_key=True, comment='股票代码')
    
    # 基本信息
    name = Column(String(50), comment='股票名称')
    industry = Column(String(50), comment='所属行业')
    
    # 交易数据
    close = Column(Float, comment='收盘价')
    pct_chg = Column(Float, comment='涨跌幅')
    amount = Column(Float, comment='成交额')
    limit_amount = Column(Float, comment='板上成交金额(涨停无此数据)')
    
    # 市值数据
    float_mv = Column(Float, comment='流通市值')
    total_mv = Column(Float, comment='总市值')
    turnover_ratio = Column(Float, comment='换手率')
    
    # 封板数据
    fd_amount = Column(Float, comment='封单金额')
    first_time = Column(String(8), comment='首次封板时间')
    last_time = Column(String(8), comment='最后封板时间')
    open_times = Column(Integer, comment='炸板次数/开板次数')
    
    # 涨停统计
    up_stat = Column(String(20), comment='涨停统计(N/T格式)')
    limit_times = Column(Integer, comment='连板数')
    limit = Column(String(1), comment='涨跌停状态(D跌停/U涨停/Z炸板)')

    @staticmethod
    def filter_by_criteria(db: Session, limit_times: Optional[int] = None, up_stat: Optional[str] = None):
        """
        根据连板次数和涨停统计筛选股票
        :param db: 数据库会话对象
        :param limit_times: 连板次数
        :param up_stat: 涨停统计 (N/T 格式)
        :return: 符合条件的股票列表
        """
        query = db.query(LimitList)
        if limit_times is not None:
            query = query.filter(LimitList.limit_times == limit_times)
        if up_stat is not None:
            query = query.filter(LimitList.up_stat == up_stat)
        return query.all()


class KplList(Base):
    """KPL涨跌停榜单数据"""
    __tablename__ = 'kpl_list'

    # 复合主键：交易日期 + 股票代码
    trade_date = Column(String(8), primary_key=True, comment='交易日期')
    ts_code = Column(String(10), primary_key=True, comment='股票代码')
    
    # 基本信息
    name = Column(String(50), comment='股票名称')
    
    # 时间信息
    lu_time = Column(String(8), comment='涨停时间')
    ld_time = Column(String(8), comment='跌停时间')
    open_time = Column(String(8), comment='开板时间')
    last_time = Column(String(8), comment='最后涨停时间')
    
    # 描述信息
    lu_desc = Column(String(500), comment='涨停原因')
    tag = Column(String(50), comment='标签')
    theme = Column(String(200), comment='板块')
    
    # 交易数据
    net_change = Column(Float, comment='主力净额(元)')
    bid_amount = Column(Float, comment='竞价成交额(元)')
    status = Column(String(20), comment='状态（N连板）')
    bid_change = Column(Float, comment='竞价成交额')
    bid_turnover = Column(Float, comment='竞价换手%')
    lu_bid_vol = Column(Float, comment='涨停委买额')
    pct_chg = Column(Float, comment='涨跌幅%')
    bid_pct_chg = Column(Float, comment='竞价涨幅%')
    rt_pct_chg = Column(Float, comment='实时涨幅%')
    limit_order = Column(Float, comment='封单')
    amount = Column(Float, comment='成交额')
    turnover_rate = Column(Float, comment='换手率%')
    free_float = Column(Float, comment='实际流通')
    lu_limit_order = Column(Float, comment='最大封单')

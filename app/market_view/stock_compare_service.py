from typing import List, Dict, Any
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db

class StockCompareService:
    def __init__(self, db: Session = None):
        self.db = next(get_db()) if db is None else db

    @staticmethod
    def get_stock_comparison(ts_code: str, compare_code: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """获取两只股票的对比数据"""
        db = next(get_db())
        try:
            # 查询第一只股票数据
            query = text("""
                SELECT trade_date, open, high, low, close, vol as volume, amount, pct_chg
                FROM stock_daily
                WHERE ts_code = :ts_code 
                AND trade_date BETWEEN :start_date AND :end_date
                ORDER BY trade_date ASC
            """)
            result = db.execute(
                query,
                {"ts_code": ts_code, "start_date": start_date, "end_date": end_date}
            )
            stock1_daily = result.fetchall()
            
            # 查询第二只股票数据
            result = db.execute(
                query,
                {"ts_code": compare_code, "start_date": start_date, "end_date": end_date}
            )
            stock2_daily = result.fetchall()

            # 查询涨跌停数据
            limit_query = text("""
                SELECT l.trade_date, k.lu_time, k.ld_time, k.status
                FROM limit_list_d l
                LEFT JOIN kpl_list k ON l.ts_code = k.ts_code AND l.trade_date = k.trade_date
                WHERE l.ts_code = :ts_code 
                AND l.trade_date BETWEEN :start_date AND :end_date
                ORDER BY l.trade_date ASC
            """)
            
            result = db.execute(
                limit_query,
                {"ts_code": ts_code, "start_date": start_date, "end_date": end_date}
            )
            stock1_limit = result.fetchall()
            
            result = db.execute(
                limit_query,
                {"ts_code": compare_code, "start_date": start_date, "end_date": end_date}
            )
            stock2_limit = result.fetchall()

            # 查询股票基本信息
            stock_info_query = text("""
                SELECT ts_code, name 
                FROM stock_basic 
                WHERE ts_code = :ts_code
            """)
            
            result = db.execute(
                stock_info_query,
                {"ts_code": ts_code}
            )
            stock1_info = result.fetchone()
            
            result = db.execute(
                stock_info_query,
                {"ts_code": compare_code}
            )
            stock2_info = result.fetchone()

            # 转换为DataFrame进行数据处理
            stock1_df = pd.DataFrame(stock1_daily, columns=['trade_date', 'open', 'high', 'low', 'close', 'volume', 'amount', 'pct_chg'])
            stock2_df = pd.DataFrame(stock2_daily, columns=['trade_date', 'open', 'high', 'low', 'close', 'volume', 'amount', 'pct_chg'])
            
            stock1_limit_df = pd.DataFrame(stock1_limit, columns=['trade_date', 'lu_time', 'ld_time', 'status'])
            stock2_limit_df = pd.DataFrame(stock2_limit, columns=['trade_date', 'lu_time', 'ld_time', 'status'])

            # 计算相对涨跌幅
            if not stock1_df.empty:
                stock1_df['relative_chg'] = (stock1_df['close'] / stock1_df['close'].iloc[0] - 1) * 100
            if not stock2_df.empty:
                stock2_df['relative_chg'] = (stock2_df['close'] / stock2_df['close'].iloc[0] - 1) * 100

            return {
                'stock1': {
                    'ts_code': stock1_info[0],
                    'name': stock1_info[1],
                    'daily': stock1_df.to_dict('records'),
                    'limit': stock1_limit_df.to_dict('records')
                },
                'stock2': {
                    'ts_code': stock2_info[0],
                    'name': stock2_info[1],
                    'daily': stock2_df.to_dict('records'),
                    'limit': stock2_limit_df.to_dict('records')
                }
            }
        finally:
            db.close()

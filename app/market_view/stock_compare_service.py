from typing import List, Dict, Any
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db

class StockCompareService:
    def __init__(self, db: Session = None):
        self.db = next(get_db()) if db is None else db

    @staticmethod
    def get_stock_comparison(
        base_stock: str,
        compare_stocks: List[str],
        start_date: str,
        end_date: str
    ) -> Dict[str, Any]:
        """获取多只股票的对比数据"""
        db = next(get_db())
        try:
            # 查询股票日线数据的SQL
            daily_query = text("""
                SELECT trade_date, open, high, low, close, vol as volume, amount, pct_chg
                FROM stock_daily
                WHERE ts_code = :ts_code 
                AND trade_date BETWEEN :start_date AND :end_date
                ORDER BY trade_date ASC
            """)

            # 查询涨跌停数据的SQL
            limit_query = text("""
                SELECT l.trade_date, k.lu_time, k.ld_time, k.status
                FROM limit_list_d l
                LEFT JOIN kpl_list k ON l.ts_code = k.ts_code AND l.trade_date = k.trade_date
                WHERE l.ts_code = :ts_code 
                AND l.trade_date BETWEEN :start_date AND :end_date
                ORDER BY l.trade_date ASC
            """)

            # 查询股票基本信息的SQL
            stock_info_query = text("""
                SELECT ts_code, name, industry, market
                FROM stock_basic 
                WHERE ts_code = :ts_code
            """)

            # 获取基准股票数据
            base_daily = pd.DataFrame(
                db.execute(
                    daily_query,
                    {"ts_code": base_stock, "start_date": start_date, "end_date": end_date}
                ).fetchall(),
                columns=['trade_date', 'open', 'high', 'low', 'close', 'volume', 'amount', 'pct_chg']
            )
            base_limit = pd.DataFrame(
                db.execute(
                    limit_query,
                    {"ts_code": base_stock, "start_date": start_date, "end_date": end_date}
                ).fetchall(),
                columns=['trade_date', 'lu_time', 'ld_time', 'status']
            )
            
            # 获取基准股票信息
            base_info_row = db.execute(
                stock_info_query,
                {"ts_code": base_stock}
            ).fetchone()
            base_info = {
                "ts_code": base_info_row.ts_code,
                "name": base_info_row.name,
                "industry": base_info_row.industry,
                "market": base_info_row.market
            }

            # 计算基准股票的相对涨跌幅
            if not base_daily.empty:
                base_daily['relative_chg'] = (base_daily['close'] / base_daily['close'].iloc[0] - 1) * 100

            # 获取所有对比股票的数据
            compare_data = []
            for ts_code in compare_stocks:
                daily_df = pd.DataFrame(
                    db.execute(
                        daily_query,
                        {"ts_code": ts_code, "start_date": start_date, "end_date": end_date}
                    ).fetchall(),
                    columns=['trade_date', 'open', 'high', 'low', 'close', 'volume', 'amount', 'pct_chg']
                )
                limit_df = pd.DataFrame(
                    db.execute(
                        limit_query,
                        {"ts_code": ts_code, "start_date": start_date, "end_date": end_date}
                    ).fetchall(),
                    columns=['trade_date', 'lu_time', 'ld_time', 'status']
                )
                
                # 获取对比股票信息
                stock_info_row = db.execute(
                    stock_info_query,
                    {"ts_code": ts_code}
                ).fetchone()
                stock_info = {
                    "ts_code": stock_info_row.ts_code,
                    "name": stock_info_row.name,
                    "industry": stock_info_row.industry,
                    "market": stock_info_row.market
                }

                # 计算相对涨跌幅
                if not daily_df.empty:
                    daily_df['relative_chg'] = (daily_df['close'] / daily_df['close'].iloc[0] - 1) * 100

                compare_data.append({
                    "ts_code": stock_info["ts_code"],
                    "name": stock_info["name"],
                    "industry": stock_info["industry"],
                    "market": stock_info["market"],
                    "daily": daily_df.to_dict('records'),
                    "limit": limit_df.to_dict('records')
                })

            return {
                "base_stock": {
                    "ts_code": base_info["ts_code"],
                    "name": base_info["name"],
                    "industry": base_info["industry"],
                    "market": base_info["market"],
                    "daily": base_daily.to_dict('records'),
                    "limit": base_limit.to_dict('records')
                },
                "compare_stocks": compare_data
            }

        except Exception as e:
            print(f"Error in get_stock_comparison: {str(e)}")
            raise e
        finally:
            db.close()

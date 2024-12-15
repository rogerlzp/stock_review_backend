from typing import List, Dict, Any
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db

class StockCompareService:
    def __init__(self, db: Session = None):
        self.db = next(get_db()) if db is None else db

    @classmethod
    def get_stock_info(cls, ts_code: str):
        """获取股票基本信息"""
        db = next(get_db())
        stock_info_query = text("""
            SELECT ts_code, name, industry, market
            FROM stock_basic 
            WHERE ts_code = :ts_code
        """)
        stock_info_row = db.execute(stock_info_query, {"ts_code": ts_code}).fetchone()
        stock_info = {
            "ts_code": stock_info_row.ts_code,
            "name": stock_info_row.name,
            "industry": stock_info_row.industry,
            "market": stock_info_row.market
        }
        return stock_info

    @classmethod
    def get_stock_comparison(cls, ts_code: str, compare_codes: List[str], start_date: str, end_date: str):
        """获取股票对比数据"""
        try:
            db = next(get_db())
            
            # 基准股票数据
            base_stock = cls.get_stock_info(ts_code)
            base_daily = db.execute(
                text("""
                    SELECT d.trade_date, d.open, d.high, d.low, d.close, 
                           d.vol, d.amount, d.pct_chg,
                           f.turnover_rate_f, f.volume_ratio, 
                           f.brar_ar_bfq, f.brar_br_bfq, f.psy_bfq, f.psyma_bfq
                    FROM stock_daily d
                    LEFT JOIN stk_factor_pro f ON d.ts_code = f.ts_code AND d.trade_date = f.trade_date
                    WHERE d.ts_code = :ts_code 
                    AND d.trade_date BETWEEN :start_date AND :end_date
                    ORDER BY d.trade_date
                """),
                {"ts_code": ts_code, "start_date": start_date, "end_date": end_date}
            ).fetchall()

            # 计算基准股票的相对涨跌幅
            base_daily_list = []
            base_price = None
            for row in base_daily:
                daily_dict = {
                    "trade_date": row.trade_date,
                    "open": float(row.open),
                    "high": float(row.high),
                    "low": float(row.low),
                    "close": float(row.close),
                    "volume": float(row.vol),
                    "amount": float(row.amount),
                    "pct_chg": float(row.pct_chg),
                    "turnover_rate": float(row.turnover_rate_f) if row.turnover_rate_f else None,
                    "volume_ratio": float(row.volume_ratio) if row.volume_ratio else None,
                    "brar_ar": float(row.brar_ar_bfq) if row.brar_ar_bfq else None,
                    "brar_br": float(row.brar_br_bfq) if row.brar_br_bfq else None,
                    "psy": float(row.psy_bfq) if row.psy_bfq else None,
                    "psyma": float(row.psyma_bfq) if row.psyma_bfq else None
                }
                
                if base_price is None:
                    base_price = daily_dict["close"]
                    daily_dict["relative_chg"] = 0
                else:
                    daily_dict["relative_chg"] = (daily_dict["close"] - base_price) / base_price * 100
                
                base_daily_list.append(daily_dict)

            base_stock["daily"] = base_daily_list
            base_stock["limit"] = []

            # 获取对比股票数据
            compare_stocks = []
            for compare_code in compare_codes:
                compare_stock = cls.get_stock_info(compare_code)
                compare_daily = db.execute(
                    text("""
                        SELECT d.trade_date, d.open, d.high, d.low, d.close, 
                               d.vol, d.amount, d.pct_chg,
                               f.turnover_rate_f, f.volume_ratio, 
                               f.brar_ar_bfq, f.brar_br_bfq, f.psy_bfq, f.psyma_bfq
                        FROM stock_daily d
                        LEFT JOIN stk_factor_pro f ON d.ts_code = f.ts_code AND d.trade_date = f.trade_date
                        WHERE d.ts_code = :ts_code 
                        AND d.trade_date BETWEEN :start_date AND :end_date
                        ORDER BY d.trade_date
                    """),
                    {"ts_code": compare_code, "start_date": start_date, "end_date": end_date}
                ).fetchall()

                compare_daily_list = []
                compare_price = None
                for row in compare_daily:
                    daily_dict = {
                        "trade_date": row.trade_date,
                        "open": float(row.open),
                        "high": float(row.high),
                        "low": float(row.low),
                        "close": float(row.close),
                        "volume": float(row.vol),
                        "amount": float(row.amount),
                        "pct_chg": float(row.pct_chg),
                        "turnover_rate": float(row.turnover_rate_f) if row.turnover_rate_f else None,
                        "volume_ratio": float(row.volume_ratio) if row.volume_ratio else None,
                        "brar_ar": float(row.brar_ar_bfq) if row.brar_ar_bfq else None,
                        "brar_br": float(row.brar_br_bfq) if row.brar_br_bfq else None,
                        "psy": float(row.psy_bfq) if row.psy_bfq else None,
                        "psyma": float(row.psyma_bfq) if row.psyma_bfq else None
                    }
                    
                    if compare_price is None:
                        compare_price = daily_dict["close"]
                        daily_dict["relative_chg"] = 0
                    else:
                        daily_dict["relative_chg"] = (daily_dict["close"] - compare_price) / compare_price * 100
                    
                    compare_daily_list.append(daily_dict)

                compare_stock["daily"] = compare_daily_list
                compare_stock["limit"] = []
                compare_stocks.append(compare_stock)

            return {
                "base_stock": base_stock,
                "compare_stocks": compare_stocks
            }

        except Exception as e:
            print("Error in get_stock_comparison:", str(e))
            raise e

from typing import List, Dict, Any
import pandas as pd
import numpy as np
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

    @classmethod
    def get_weekly_analysis(cls, ts_code: str, start_date: str, end_date: str):
        """获取股票的周度分析数据"""
        try:
            db = next(get_db())
            
            # 获取股票基本信息
            stock_info = cls.get_stock_info(ts_code)
            
            # 查询日线数据，包括技术指标和资金流向
            daily_data = db.execute(
                text("""
                    WITH daily_stats AS (
                        SELECT 
                            d.trade_date,
                            d.open,
                            d.high,
                            d.low,
                            d.close,
                            d.vol as volume,
                            d.amount,
                            d.pct_chg,
                            EXTRACT(DOW FROM TO_DATE(d.trade_date, 'YYYYMMDD')) as day_of_week,
                            TO_CHAR(TO_DATE(d.trade_date, 'YYYYMMDD'), 'IYYY-IW') as year_week,
                            f.turnover_rate_f,
                            f.volume_ratio,
                            f.brar_ar_bfq,
                            f.brar_br_bfq,
                            f.psy_bfq,
                            f.psyma_bfq,
                            m.net_mf_amount,
                            m.buy_sm_vol,
                            m.sell_sm_vol,
                            m.buy_md_vol,
                            m.sell_md_vol,
                            m.buy_lg_vol,
                            m.sell_lg_vol,
                            m.buy_elg_vol,
                            m.sell_elg_vol
                        FROM stock_daily d
                        LEFT JOIN stk_factor_pro f ON d.ts_code = f.ts_code AND d.trade_date = f.trade_date
                        LEFT JOIN moneyflow m ON d.ts_code = m.ts_code AND d.trade_date = m.trade_date
                        WHERE d.ts_code = :ts_code 
                        AND d.trade_date BETWEEN :start_date AND :end_date
                    )
                    SELECT 
                        year_week,
                        day_of_week,
                        COUNT(*) as day_count,
                        SUM(CASE WHEN pct_chg > 0 THEN 1 ELSE 0 END) as up_days,
                        SUM(CASE WHEN pct_chg < 0 THEN 1 ELSE 0 END) as down_days,
                        AVG(pct_chg) as avg_pct_chg,
                        AVG(volume) as avg_volume,
                        AVG(turnover_rate_f) as avg_turnover,
                        AVG(volume_ratio) as avg_volume_ratio,
                        AVG(net_mf_amount) as avg_net_flow,
                        AVG(buy_sm_vol - sell_sm_vol) as small_flow,
                        AVG(buy_md_vol - sell_md_vol) as medium_flow,
                        AVG(buy_lg_vol - sell_lg_vol) as large_flow,
                        AVG(buy_elg_vol - sell_elg_vol) as extra_large_flow,
                        json_agg(json_build_object(
                            'trade_date', trade_date,
                            'open', open,
                            'high', high,
                            'low', low,
                            'close', close,
                            'volume', volume,
                            'pct_chg', pct_chg,
                            'turnover_rate', turnover_rate_f,
                            'volume_ratio', volume_ratio,
                            'brar_ar', brar_ar_bfq,
                            'brar_br', brar_br_bfq,
                            'psy', psy_bfq,
                            'psyma', psyma_bfq,
                            'net_flow', net_mf_amount
                        ) ORDER BY trade_date) as daily_details
                    FROM daily_stats
                    GROUP BY year_week, day_of_week
                    ORDER BY year_week, day_of_week
                """),
                {"ts_code": ts_code, "start_date": start_date, "end_date": end_date}
            ).fetchall()

            # 处理查询结果
            weekly_analysis = {}
            for row in daily_data:
                year_week = row.year_week
                if year_week not in weekly_analysis:
                    weekly_analysis[year_week] = {
                        "weekdays": {},
                        "summary": {
                            "up_days": 0,
                            "down_days": 0,
                            "total_days": 0,
                            "avg_volume": 0,
                            "avg_turnover": 0,
                            "avg_net_flow": 0
                        }
                    }
                
                day_data = {
                    "day_count": row.day_count,
                    "up_days": row.up_days,
                    "down_days": row.down_days,
                    "avg_pct_chg": float(row.avg_pct_chg) if row.avg_pct_chg else 0,
                    "avg_volume": float(row.avg_volume) if row.avg_volume else 0,
                    "avg_turnover": float(row.avg_turnover) if row.avg_turnover else 0,
                    "avg_volume_ratio": float(row.avg_volume_ratio) if row.avg_volume_ratio else 0,
                    "avg_net_flow": float(row.avg_net_flow) if row.avg_net_flow else 0,
                    "flow_distribution": {
                        "small": float(row.small_flow) if row.small_flow else 0,
                        "medium": float(row.medium_flow) if row.medium_flow else 0,
                        "large": float(row.large_flow) if row.large_flow else 0,
                        "extra_large": float(row.extra_large_flow) if row.extra_large_flow else 0
                    },
                    "daily_details": row.daily_details
                }
                
                weekday = row.day_of_week
                weekly_analysis[year_week]["weekdays"][weekday] = day_data
                
                # 更新周汇总数据
                summary = weekly_analysis[year_week]["summary"]
                summary["up_days"] += row.up_days
                summary["down_days"] += row.down_days
                summary["total_days"] += row.day_count
                summary["avg_volume"] += float(row.avg_volume) if row.avg_volume else 0
                summary["avg_turnover"] += float(row.avg_turnover) if row.avg_turnover else 0
                summary["avg_net_flow"] += float(row.avg_net_flow) if row.avg_net_flow else 0

            # 计算周平均值
            for week_data in weekly_analysis.values():
                summary = week_data["summary"]
                if summary["total_days"] > 0:
                    summary["avg_volume"] /= summary["total_days"]
                    summary["avg_turnover"] /= summary["total_days"]
                    summary["avg_net_flow"] /= summary["total_days"]

            return {
                "stock_info": stock_info,
                "weekly_analysis": weekly_analysis
            }

        except Exception as e:
            print("Error in get_weekly_analysis:", str(e))
            raise e

    @classmethod
    def get_weekly_pattern(cls, ts_code: str, start_date: str = None, end_date: str = None):
        """获取股票周度交易规律分析"""
        try:
            db = next(get_db())
            
            # 构建查询条件
            date_condition = ""
            params = {"ts_code": ts_code}
            if start_date and end_date:
                date_condition = "AND d.trade_date::varchar BETWEEN :start_date AND :end_date"
                params.update({"start_date": start_date, "end_date": end_date})
            
            # 获取每日交易数据和资金流向数据
            query = text(f"""
                SELECT 
                    d.trade_date,
                    d.open, d.high, d.low, d.close,
                    d.vol, d.amount, d.pct_chg,
                    EXTRACT(DOW FROM d.trade_date::date) as weekday,
                    TO_CHAR(d.trade_date::date, 'IYYY-IW') as yearweek,
                    m.net_amount,
                    m.net_amount_rate,
                    m.buy_elg_amount,
                    m.buy_lg_amount,
                    m.buy_md_amount,
                    m.buy_sm_amount,
                    m.buy_elg_amount_rate,
                    m.buy_lg_amount_rate,
                    m.buy_md_amount_rate,
                    m.buy_sm_amount_rate
                FROM stock_daily d
                LEFT JOIN moneyflow_dc m ON d.ts_code = m.ts_code AND d.trade_date::varchar = m.trade_date::varchar
                WHERE d.ts_code = :ts_code {date_condition}
                ORDER BY d.trade_date
            """)
            
            rows = db.execute(query, params).fetchall()
            if not rows:
                return {"error": "No data found"}
            
            # 将 SQLAlchemy Row 对象转换为字典列表
            data = []
            for row in rows:
                row_dict = {}
                for column in row._mapping:
                    row_dict[column] = row._mapping[column]
                data.append(row_dict)
            
            # 转换为DataFrame进行分析
            df = pd.DataFrame(data)
            
            # 处理无效的浮点数值
            def clean_float(x):
                if pd.isna(x) or (isinstance(x, (int, float)) and np.isinf(x)):
                    return 0.0
                try:
                    return float(x)
                except:
                    return 0.0
            
            # 确保数值类型列是有效的 float
            numeric_columns = ['open', 'high', 'low', 'close', 'vol', 'amount', 'pct_chg', 
                             'net_amount', 'net_amount_rate', 'buy_elg_amount', 'buy_lg_amount', 
                             'buy_md_amount', 'buy_sm_amount', 'buy_elg_amount_rate', 
                             'buy_lg_amount_rate', 'buy_md_amount_rate', 'buy_sm_amount_rate']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = df[col].apply(clean_float)
            
            # 确保日期列是字符串
            df['trade_date'] = df['trade_date'].astype(str)
            
            # 1. 计算每个交易日的统计特征
            weekly_patterns = []
            for weekday in range(1, 6):  # 1-5 对应周一到周五
                day_data = df[df['weekday'] == weekday]
                if len(day_data) == 0:
                    continue
                
                pattern = {
                    "weekday": int(weekday),
                    "trading_count": int(len(day_data)),
                    "up_count": int(len(day_data[day_data['pct_chg'] > 0])),
                    "down_count": int(len(day_data[day_data['pct_chg'] < 0])),
                    "avg_chg": clean_float(day_data['pct_chg'].mean()),
                    "max_up": clean_float(day_data['pct_chg'].max()),
                    "max_down": clean_float(day_data['pct_chg'].min()),
                    "avg_vol": clean_float(day_data['vol'].mean()),
                    "avg_amount": clean_float(day_data['amount'].mean()),
                    "money_flow": {
                        "net_amount": clean_float(day_data['net_amount'].mean()) if 'net_amount' in day_data else 0.0,
                        "super_large": clean_float(day_data['buy_elg_amount'].mean()) if 'buy_elg_amount' in day_data else 0.0,
                        "large": clean_float(day_data['buy_lg_amount'].mean()) if 'buy_lg_amount' in day_data else 0.0,
                        "medium": clean_float(day_data['buy_md_amount'].mean()) if 'buy_md_amount' in day_data else 0.0,
                        "small": clean_float(day_data['buy_sm_amount'].mean()) if 'buy_sm_amount' in day_data else 0.0
                    }
                }
                weekly_patterns.append(pattern)
            
            # 2. 计算周度趋势
            weekly_trends = []
            for yearweek, week_data in df.groupby('yearweek'):
                trend = {
                    "yearweek": str(yearweek),
                    "avg_chg": clean_float(week_data['pct_chg'].mean()),
                    "total_vol": clean_float(week_data['vol'].sum()),
                    "total_amount": clean_float(week_data['amount'].sum()),
                    "money_flow": {
                        "net_amount": clean_float(week_data['net_amount'].sum()) if 'net_amount' in week_data else 0.0,
                        "super_large": clean_float(week_data['buy_elg_amount'].sum()) if 'buy_elg_amount' in week_data else 0.0,
                        "large": clean_float(week_data['buy_lg_amount'].sum()) if 'buy_lg_amount' in week_data else 0.0,
                        "medium": clean_float(week_data['buy_md_amount'].sum()) if 'buy_md_amount' in week_data else 0.0,
                        "small": clean_float(week_data['buy_sm_amount'].sum()) if 'buy_sm_amount' in week_data else 0.0
                    },
                    "daily_stats": []
                }
                
                # 添加每日统计
                for _, day_data in week_data.iterrows():
                    trend["daily_stats"].append({
                        "date": str(day_data['trade_date']),
                        "weekday": int(day_data['weekday']),
                        "pct_chg": clean_float(day_data['pct_chg']),
                        "amount": clean_float(day_data['amount'])
                    })
                
                weekly_trends.append(trend)
            
            # 3. 计算整体统计
            period_summary = {
                "total_days": int(len(df)),
                "up_days": int(len(df[df['pct_chg'] > 0])),
                "down_days": int(len(df[df['pct_chg'] < 0])),
                "avg_daily_vol": clean_float(df['vol'].mean()),
                "avg_daily_amount": clean_float(df['amount'].mean()),
                "max_up": clean_float(df['pct_chg'].max()),
                "max_down": clean_float(df['pct_chg'].min()),
                "win_rate": clean_float(len(df[df['pct_chg'] > 0]) / len(df) * 100)
            }
            
            return {
                "period_summary": period_summary,
                "weekly_patterns": weekly_patterns,
                "weekly_trends": weekly_trends
            }
            
        except Exception as e:
            return {"error": str(e)}

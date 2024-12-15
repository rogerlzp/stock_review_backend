from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db
from loguru import logger
from datetime import datetime
from app.db.session import async_session

logger = logger.bind(module=__name__)

class MarketReviewService:
    def __init__(self, db: Session = None):
        self.db = next(get_db()) if db is None else db
    
    def get_limit_up_stocks(
        self,
        trade_date: str,
        limit_times: Optional[int] = None,
        up_stat: Optional[str] = None
    ):
        """获取涨停板数据，支持连板和涨停统计过滤"""
        # 构建基础查询
        query = """
            SELECT DISTINCT 
                l.ts_code, l.name, l.trade_date, l.limit_times,
                k.lu_time, k.ld_time, k.open_time, k.last_time,
                k.lu_desc, k.tag, k.theme, k.net_change,
                k.bid_amount, k.status, k.bid_change,
                k.bid_turnover, k.lu_bid_vol, k.pct_chg,
                k.bid_pct_chg, k.rt_pct_chg, k.limit_order,
                k.amount, k.turnover_rate, k.free_float,
                k.lu_limit_order
            FROM limit_list_d l
            LEFT JOIN kpl_list k ON l.ts_code = k.ts_code 
                AND l.trade_date = k.trade_date
            WHERE l.trade_date = :trade_date
                AND l.limit = 'U'  -- 只查询涨停
        """
        
        params = {"trade_date": trade_date}
        
        # 添加连板次数过滤
        if limit_times is not None:
            query += " AND l.limit_times = :limit_times"
            params["limit_times"] = limit_times
        
        # 添加涨停统计过滤
        if up_stat is not None:
            query += " AND l.up_stat = :up_stat"
            params["up_stat"] = up_stat
        
        # 执行查询
        result = self.db.execute(text(query), params)
        stocks = result.fetchall()
        
        # 转换为字典列表并处理数值格式
        return [
            {
                **dict(row._mapping),
                'amount': float(row._mapping.amount) if row._mapping.amount else 0,
                'turnover_rate': float(row._mapping.turnover_rate) if row._mapping.turnover_rate else 0,
                'pct_chg': float(row._mapping.pct_chg) if row._mapping.pct_chg else 0,
            }
            for row in stocks
        ]
    
    def get_daily_review(self, trade_date: str) -> Dict[str, Any]:
        """获取每日市场复盘数据"""
        formatted_date = trade_date.replace('-', '')
        
        return {
            "hot_sectors": self._get_hot_sectors(formatted_date),
            "capital_flow": self._get_capital_flow(formatted_date),
            "market_stats": self._get_market_statistics(formatted_date),
            "limit_up_analysis": self._get_limit_up_analysis(formatted_date),
            "concept_analysis": self._get_concept_analysis(formatted_date)
        }
    
    def _get_hot_sectors(self, trade_date: str) -> List[Dict]:
        """获取热门板块数据"""
        query = text("""
            WITH sector_stats AS (
                SELECT 
                    c.concept_name,
                    COUNT(DISTINCT CASE WHEN d.pct_chg >= 9.5 THEN d.ts_code END) as limit_up_count,
                    AVG(d.pct_chg) as avg_change,
                    COUNT(DISTINCT d.ts_code) as total_stocks
                FROM stock_daily d
                JOIN stock_concept_detail c ON d.ts_code = c.ts_code
                WHERE d.trade_date = :trade_date
                GROUP BY c.concept_name
            )
            SELECT 
                concept_name,
                limit_up_count,
                avg_change,
                total_stocks,
                (limit_up_count::float / total_stocks) as limit_up_ratio
            FROM sector_stats
            WHERE total_stocks >= 5
            ORDER BY limit_up_ratio DESC, avg_change DESC
            LIMIT 10
        """)
        
        return [dict(row) for row in self.db.execute(query, {"trade_date": trade_date})]
    
    def _get_capital_flow(self, trade_date: str) -> List[Dict]:
        """获取资金流向数据"""
        query = text("""
            SELECT 
                s.name,
                d.ts_code,
                d.amount,
                d.vol,
                d.pct_chg,
                d.close,
                d.amount / LAG(d.amount) OVER (PARTITION BY d.ts_code ORDER BY d.trade_date) as amount_ratio
            FROM stock_daily d
            JOIN stock_basic s ON d.ts_code = s.ts_code
            WHERE d.trade_date = :trade_date
            ORDER BY amount DESC
            LIMIT 20
        """)
        
        return [dict(row) for row in self.db.execute(query, {"trade_date": trade_date})]
    
    def _get_market_statistics(self, trade_date: str) -> Dict:
        """获取市场整体统计数据"""
        query = text("""
            SELECT 
                COUNT(CASE WHEN pct_chg > 0 THEN 1 END) as up_count,
                COUNT(CASE WHEN pct_chg < 0 THEN 1 END) as down_count,
                COUNT(CASE WHEN pct_chg >= 9.5 THEN 1 END) as limit_up_count,
                COUNT(CASE WHEN pct_chg <= -9.5 THEN 1 END) as limit_down_count,
                COUNT(CASE WHEN pct_chg >= 5 THEN 1 END) as up_5_percent,
                COUNT(CASE WHEN pct_chg <= -5 THEN 1 END) as down_5_percent,
                SUM(amount) as total_amount
            FROM stock_daily
            WHERE trade_date = :trade_date
        """)
        
        return dict(self.db.execute(query, {"trade_date": trade_date}).first())
    
    def _get_limit_up_analysis(self, trade_date: str) -> Dict[str, Any]:
        """获取涨停板分析
        
        返回数据包括：
        1. 涨停板统计：首板/二板/三板及以上数量
        2. 行业涨停分布
        3. 最强涨停股（按封单金额排序）
        4. 最快涨停股（按首次封板时间排序）
        5. 最后涨停股（尾盘拉升）
        6. 炸板股票统计
        7. 异动分析
        8. 连板趋势分析
        9. 强势股跟踪
        10. 板块联动分析
        """
        # 1. 涨停板统计
        limit_stats_query = text("""
            SELECT 
                limit_times,
                COUNT(*) as count
            FROM limit_list
            WHERE trade_date = :trade_date
            AND limit = 'U'
            GROUP BY limit_times
            ORDER BY limit_times
        """)
        
        # 2. 行业涨停分布
        industry_stats_query = text("""
            SELECT 
                industry,
                COUNT(*) as limit_up_count,
                STRING_AGG(name, ',') as stock_names
            FROM limit_list
            WHERE trade_date = :trade_date
            AND limit = 'U'
            GROUP BY industry
            ORDER BY limit_up_count DESC
            LIMIT 10
        """)
        
        # 3. 最强涨停股
        strongest_query = text("""
            SELECT 
                ts_code,
                name,
                industry,
                fd_amount,
                limit_times,
                turnover_ratio,
                up_stat
            FROM limit_list
            WHERE trade_date = :trade_date
            AND limit = 'U'
            ORDER BY fd_amount DESC
            LIMIT 10
        """)
        
        # 4. 最快涨停股
        fastest_query = text("""
            SELECT 
                ts_code,
                name,
                industry,
                first_time,
                fd_amount,
                limit_times
            FROM limit_list
            WHERE trade_date = :trade_date
            AND limit = 'U'
            ORDER BY first_time
            LIMIT 10
        """)
        
        # 5. 最后涨停股
        last_query = text("""
            SELECT 
                ts_code,
                name,
                industry,
                last_time,
                fd_amount,
                limit_times
            FROM limit_list
            WHERE trade_date = :trade_date
            AND limit = 'U'
            AND last_time >= '14:30:00'
            ORDER BY last_time DESC
            LIMIT 10
        """)
        
        # 6. 炸板股统计
        broken_query = text("""
            SELECT 
                ts_code,
                name,
                industry,
                open_times,
                first_time,
                pct_chg
            FROM limit_list
            WHERE trade_date = :trade_date
            AND limit = 'Z'
            ORDER BY open_times DESC
            LIMIT 10
        """)
        
        # 7. 异动分析
        abnormal_query = text("""
            WITH prev_data AS (
                SELECT 
                    l1.ts_code,
                    l1.name,
                    l1.industry,
                    l1.amount,
                    l1.turnover_ratio,
                    l1.pct_chg,
                    AVG(l2.amount) as avg_amount_5d,
                    AVG(l2.turnover_ratio) as avg_turnover_5d
                FROM limit_list l1
                LEFT JOIN limit_list l2 ON l1.ts_code = l2.ts_code
                    AND l2.trade_date < :trade_date
                    AND l2.trade_date >= (
                        SELECT MAX(trade_date)
                        FROM (
                            SELECT DISTINCT trade_date 
                            FROM limit_list 
                            WHERE trade_date < :trade_date
                            ORDER BY trade_date DESC 
                            LIMIT 5
                        ) t
                    )
                WHERE l1.trade_date = :trade_date
                GROUP BY l1.ts_code, l1.name, l1.industry, l1.amount, 
                         l1.turnover_ratio, l1.pct_chg
            )
            SELECT 
                ts_code,
                name,
                industry,
                amount,
                turnover_ratio,
                pct_chg,
                (amount / NULLIF(avg_amount_5d, 0)) as amount_ratio,
                (turnover_ratio / NULLIF(avg_turnover_5d, 0)) as turnover_ratio_change
            FROM prev_data
            WHERE (amount / NULLIF(avg_amount_5d, 0)) > 3  -- 成交额放大3倍
               OR turnover_ratio > 15  -- 换手率超15%
            ORDER BY amount_ratio DESC
            LIMIT 20
        """)
        
        # 8. 连板趋势分析
        trend_query = text("""
            WITH daily_stats AS (
                SELECT 
                    trade_date,
                    COUNT(CASE WHEN limit_times = 1 THEN 1 END) as first_board,
                    COUNT(CASE WHEN limit_times = 2 THEN 1 END) as second_board,
                    COUNT(CASE WHEN limit_times >= 3 THEN 1 END) as third_plus_board,
                    COUNT(CASE WHEN limit = 'Z' THEN 1 END) as broken_board
                FROM limit_list
                WHERE trade_date <= :trade_date
                AND trade_date >= (
                    SELECT MAX(trade_date)
                    FROM (
                        SELECT DISTINCT trade_date 
                        FROM limit_list 
                        WHERE trade_date < :trade_date
                        ORDER BY trade_date DESC 
                        LIMIT 10
                    ) t
                )
                GROUP BY trade_date
                ORDER BY trade_date
            )
            SELECT * FROM daily_stats
        """)
        
        # 9. 强势股跟踪
        strong_stocks_query = text("""
            WITH consecutive_days AS (
                SELECT 
                    l1.ts_code,
                    l1.name,
                    l1.industry,
                    COUNT(*) as up_days,
                    SUM(l1.pct_chg) as total_gain,
                    STRING_AGG(
                        CASE 
                            WHEN l1.limit = 'U' THEN '涨停'
                            WHEN l1.limit = 'Z' THEN '炸板'
                            ELSE ROUND(l1.pct_chg::numeric, 2)::text || '%'
                        END,
                        '->' ORDER BY l1.trade_date
                    ) as trend
                FROM limit_list l1
                WHERE l1.trade_date <= :trade_date
                AND l1.trade_date >= (
                    SELECT MAX(trade_date)
                    FROM (
                        SELECT DISTINCT trade_date 
                        FROM limit_list 
                        WHERE trade_date < :trade_date
                        ORDER BY trade_date DESC 
                        LIMIT 5
                    ) t
                )
                AND (l1.pct_chg >= 5 OR l1.limit IN ('U', 'Z'))
                GROUP BY l1.ts_code, l1.name, l1.industry
                HAVING COUNT(*) >= 3  -- 连续3天以上强势
            )
            SELECT 
                ts_code,
                name,
                industry,
                up_days,
                total_gain,
                trend
            FROM consecutive_days
            ORDER BY total_gain DESC
            LIMIT 20
        """)
        
        # 10. 板块联动分析
        sector_linkage_query = text("""
            WITH sector_stats AS (
                SELECT 
                    l1.industry,
                    COUNT(DISTINCT l1.ts_code) as stock_count,
                    COUNT(DISTINCT CASE WHEN l1.limit = 'U' THEN l1.ts_code END) as limit_up_count,
                    AVG(l1.pct_chg) as avg_change,
                    STRING_AGG(
                        CASE WHEN l1.limit = 'U' THEN l1.name END,
                        ',' ORDER BY l1.first_time
                    ) as limit_up_stocks
                FROM limit_list l1
                WHERE l1.trade_date = :trade_date
                GROUP BY l1.industry
                HAVING COUNT(DISTINCT CASE WHEN l1.limit = 'U' THEN l1.ts_code END) >= 2
            )
            SELECT 
                industry,
                stock_count,
                limit_up_count,
                avg_change,
                limit_up_stocks,
                (limit_up_count::float / NULLIF(stock_count, 0) * 100) as limit_up_ratio
            FROM sector_stats
            ORDER BY limit_up_ratio DESC, avg_change DESC
            LIMIT 15
        """)
        
        result = {
            "limit_stats": [dict(row) for row in self.db.execute(limit_stats_query, {"trade_date": trade_date})],
            "industry_distribution": [dict(row) for row in self.db.execute(industry_stats_query, {"trade_date": trade_date})],
            "strongest_stocks": [dict(row) for row in self.db.execute(strongest_query, {"trade_date": trade_date})],
            "fastest_stocks": [dict(row) for row in self.db.execute(fastest_query, {"trade_date": trade_date})],
            "last_stocks": [dict(row) for row in self.db.execute(last_query, {"trade_date": trade_date})],
            "broken_stocks": [dict(row) for row in self.db.execute(broken_query, {"trade_date": trade_date})],
            "abnormal_stocks": [dict(row) for row in self.db.execute(abnormal_query, {"trade_date": trade_date})],
            "board_trend": [dict(row) for row in self.db.execute(trend_query, {"trade_date": trade_date})],
            "strong_stocks": [dict(row) for row in self.db.execute(strong_stocks_query, {"trade_date": trade_date})],
            "sector_linkage": [dict(row) for row in self.db.execute(sector_linkage_query, {"trade_date": trade_date})]
        }
        
        return result
    
    def _get_concept_analysis(self, trade_date: str) -> List[Dict]:
        """获取概念分析"""
        query = text("""
            WITH concept_stats AS (
                SELECT 
                    c.concept_name,
                    COUNT(DISTINCT d.ts_code) as stock_count,
                    AVG(d.pct_chg) as avg_change,
                    MAX(d.pct_chg) as max_change,
                    STRING_AGG(DISTINCT 
                        CASE WHEN d.pct_chg >= 9.5 
                        THEN s.name 
                        END, 
                        ',' ORDER BY s.name
                    ) as limit_up_stocks
                FROM stock_daily d
                JOIN stock_concept_detail c ON d.ts_code = c.ts_code
                JOIN stock_basic s ON d.ts_code = s.ts_code
                WHERE d.trade_date = :trade_date
                GROUP BY c.concept_name
            )
            SELECT *
            FROM concept_stats
            WHERE avg_change >= 3
            ORDER BY avg_change DESC
            LIMIT 15
        """)
        
        return [dict(row) for row in self.db.execute(query, {"trade_date": trade_date})]
    
    def get_market_trend(self, index_code: str, start_date: str, end_date: str, metrics: List[str]) -> Dict[str, Any]:
        """获取指数的时间序列趋势数据
        
        Args:
            index_code: 指数代码，如：000001.SH（上证指数）
            start_date: 开始日期，格式：YYYYMMDD
            end_date: 结束日期，格式：YYYYMMDD
            metrics: 指标列表，可选值：
                    - total_mv: 总市值
                    - float_mv: 流通市值
                    - turnover_rate: 换手率
                    - pe: 市盈率
                    - pe_ttm: 市盈率TTM
                    - pb: 市净率
        """
        query = text("""
            WITH daily_metrics AS (
                SELECT 
                    trade_date,
                    total_mv,
                    float_mv,
                    turnover_rate,
                    pe,
                    pe_ttm,
                    pb
                FROM index_dailybasic
                WHERE ts_code = :index_code
                AND trade_date BETWEEN :start_date AND :end_date
                ORDER BY trade_date
            ),
            ggt_metrics AS (
                SELECT 
                    trade_date,
                    buy_amount - sell_amount as net_buy_amount
                FROM ggt_daily
                WHERE trade_date BETWEEN :start_date AND :end_date
            ),
            margin_metrics AS (
                SELECT 
                    trade_date,
                    SUM(rzrqye) as total_margin
                FROM margin
                WHERE trade_date BETWEEN :start_date AND :end_date
                GROUP BY trade_date
            )
            SELECT 
                d.trade_date,
                d.total_mv,
                d.float_mv,
                d.turnover_rate,
                d.pe,
                d.pe_ttm,
                d.pb,
                g.net_buy_amount,
                m.total_margin
            FROM daily_metrics d
            LEFT JOIN ggt_metrics g ON d.trade_date = g.trade_date
            LEFT JOIN margin_metrics m ON d.trade_date = m.trade_date
            ORDER BY d.trade_date;
        """)
        
        result = self.db.execute(query, {
            "index_code": index_code,
            "start_date": start_date,
            "end_date": end_date
        })
        
        # 初始化结果字典
        trend_data = {
            "dates": [],
            "metrics": {metric: [] for metric in metrics}
        }
        
        # 处理查询结果
        for row in result:
            trend_data["dates"].append(row.trade_date.strftime("%Y-%m-%d"))
            for metric in metrics:
                if metric in row.keys():
                    value = getattr(row, metric)
                    # 处理金额单位，转换为亿元
                    if metric in ["total_mv", "float_mv"]:
                        value = round(value / 100000000, 2)
                    trend_data["metrics"][metric].append(value)
        
        return trend_data

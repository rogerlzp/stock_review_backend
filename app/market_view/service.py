from typing import List, Dict, Any
from datetime import date
from app.database import engine
import pandas as pd
from loguru import logger

class MarketReviewService:
    @staticmethod
    async def get_market_overview(trade_date: str) -> Dict[str, Any]:
        """获取市场概览数据"""
        logger.info(f"Getting market overview data for date: {trade_date}")
        try:
            sql = """
            SELECT ts_code, close, change, pct_chg, vol, amount, turnover_rate
            FROM stock_daily
            WHERE trade_date = %(trade_date)s 
            AND ts_code IN ('000001.SH', '399001.SZ', '399006.SZ')
            """
            logger.debug(f"Executing SQL: {sql}")
            logger.debug(f"Parameters: {{'trade_date': {trade_date}}}")
            
            df = pd.read_sql(sql, engine, params={'trade_date': trade_date})
            logger.debug(f"Query result: {df.to_dict('records')}")
            return df.to_dict('records')
        except Exception as e:
            logger.error(f"Error getting market overview: {str(e)}")
            raise

    @staticmethod
    async def get_sector_flow(trade_date: str) -> List[Dict[str, Any]]:
        """获取板块资金流向"""
        logger.info(f"Getting sector flow data for date: {trade_date}")
        try:
            sql = """
            SELECT 
                name,
                pct_change,
                net_amount,
                net_amount_rate,
                buy_elg_amount,
                buy_lg_amount,
                buy_md_amount,
                buy_sm_amount,
                buy_sm_amount_stock as hot_stock
            FROM moneyflow_ind_dc
            WHERE trade_date = %(trade_date)s
            ORDER BY net_amount DESC
            LIMIT 10
            """
            logger.debug(f"Executing SQL: {sql}")
            logger.debug(f"Parameters: {{'trade_date': {trade_date}}}")
            
            df = pd.read_sql(sql, engine, params={'trade_date': trade_date})
            logger.debug(f"Query result shape: {df.shape}")
            return df.to_dict('records')
        except Exception as e:
            logger.error(f"Error getting sector flow: {str(e)}")
            raise

    @staticmethod
    async def get_top_list(trade_date: str) -> List[Dict[str, Any]]:
        """获取龙虎榜数据"""
        logger.info(f"Getting top list data for date: {trade_date}")
        try:
            sql = """
            SELECT 
                t.ts_code,
                t.name,
                t.close,
                t.pct_change,
                t.turnover_rate,
                t.l_buy,
                t.l_sell,
                t.net_amount,
                t.reason,
                i.exalter,
                i.buy,
                i.sell,
                i.net_buy
            FROM top_list t
            LEFT JOIN top_inst i ON t.ts_code = i.ts_code 
                AND t.trade_date = i.trade_date
            WHERE t.trade_date = %(trade_date)s
            ORDER BY t.net_amount DESC
            """
            logger.debug(f"Executing SQL: {sql}")
            logger.debug(f"Parameters: {{'trade_date': {trade_date}}}")
            
            df = pd.read_sql(sql, engine, params={'trade_date': trade_date})
            logger.debug(f"Query result shape: {df.shape}")
            return df.to_dict('records')
        except Exception as e:
            logger.error(f"Error getting top list: {str(e)}")
            raise

    @staticmethod
    async def get_limit_up(trade_date: str) -> List[Dict[str, Any]]:
        """获取涨停板数据"""
        logger.info(f"Getting limit up data for date: {trade_date}")
        try:
            sql = """
            SELECT 
                ts_code,
                name,
                lu_time,
                open_time,
                last_time,
                lu_desc,
                theme,
                net_change,
                status,
                turnover_rate,
                lu_limit_order,
                bid_amount,
                bid_turnover,
                amount,
                free_float
            FROM kpl_list
            WHERE trade_date = %(trade_date)s
            AND lu_time IS NOT NULL
            ORDER BY 
                CASE 
                    WHEN status LIKE '%连板%' THEN 1
                    ELSE 2
                END,
                lu_time
            """
            logger.debug(f"Executing SQL: {sql}")
            logger.debug(f"Parameters: {{'trade_date': {trade_date}}}")
            
            df = pd.read_sql(sql, engine, params={'trade_date': trade_date})
            logger.debug(f"Query result shape: {df.shape}")
            return df.to_dict('records')
        except Exception as e:
            logger.error(f"Error getting limit up data: {str(e)}")
            raise

    @staticmethod
    async def get_technical(trade_date: str) -> List[Dict[str, Any]]:
        """获取技术指标数据"""
        logger.info(f"Getting technical data for date: {trade_date}")
        try:
            sql = """
            SELECT 
                ts_code,
                close,
                macd_bfq,
                macd_dea_bfq,
                macd_dif_bfq,
                kdj_k_bfq,
                kdj_d_bfq,
                kdj_bfq,
                rsi_bfq_6,
                rsi_bfq_12,
                rsi_bfq_24,
                boll_upper_bfq,
                boll_mid_bfq,
                boll_lower_bfq,
                ma_bfq_5,
                ma_bfq_10,
                ma_bfq_20,
                ma_bfq_60,
                vol,
                amount,
                turnover_rate
            FROM stk_factor_pro
            WHERE trade_date = %(trade_date)s
            AND ts_code IN (
                SELECT ts_code FROM top_list 
                WHERE trade_date = %(trade_date)s
            )
            """
            logger.debug(f"Executing SQL: {sql}")
            logger.debug(f"Parameters: {{'trade_date': {trade_date}}}")
            
            df = pd.read_sql(sql, engine, params={'trade_date': trade_date})
            logger.debug(f"Query result shape: {df.shape}")
            return df.to_dict('records')
        except Exception as e:
            logger.error(f"Error getting technical data: {str(e)}")
            raise

    @staticmethod
    async def get_concepts(trade_date: str) -> List[Dict[str, Any]]:
        """获取概念题材数据"""
        logger.info(f"Getting concept data for date: {trade_date}")
        try:
            sql = """
            WITH hot_concepts AS (
                SELECT 
                    k.ts_code,
                    k.name,
                    k.z_t_num,
                    k.up_num,
                    COUNT(c.cons_code) as stock_count,
                    STRING_AGG(c.cons_name, ',') as cons_list,
                    MAX(c.hot_num) as hot_num,
                    MAX(c.description) as description
                FROM kpl_concept k
                LEFT JOIN kpl_concept_cons c 
                    ON k.ts_code = c.ts_code 
                    AND k.trade_date = %(trade_date)s
                WHERE k.trade_date = %(trade_date)s
                GROUP BY k.ts_code, k.name, k.z_t_num, k.up_num
                ORDER BY k.z_t_num DESC, k.up_num DESC
            )
            SELECT * FROM hot_concepts LIMIT 10
            """
            logger.debug(f"Executing SQL: {sql}")
            logger.debug(f"Parameters: {{'trade_date': {trade_date}}}")
            
            # 使用字典形式传递参数
            params = {'trade_date': trade_date}
            df = pd.read_sql(sql, engine, params=params)
            
            logger.debug(f"Query result shape: {df.shape}")
            logger.debug(f"Query result columns: {df.columns}")
            if not df.empty:
                logger.debug(f"First row: {df.iloc[0].to_dict()}")
            else:
                logger.warning("Query returned no results")
            
            return df.to_dict('records')
        except Exception as e:
            logger.error(f"Error getting concept data: {str(e)}", exc_info=True)
            # 打印完整的错误堆栈
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            raise

    @staticmethod
    async def get_daily_review(trade_date: str) -> Dict[str, Any]:
        """获取完整的每日复盘数据"""
        try:
            overview = await MarketReviewService.get_market_overview(trade_date)
            sector_flow = await MarketReviewService.get_sector_flow(trade_date)
            top_list = await MarketReviewService.get_top_list(trade_date)
            concepts = await MarketReviewService.get_concepts(trade_date)
            limit_up = await MarketReviewService.get_limit_up(trade_date)
            technical = await MarketReviewService.get_technical(trade_date)
            
            return {
                "date": trade_date,
                "market_overview": overview,
                "sector_flow": sector_flow,
                "top_list": top_list,
                "concepts": concepts,
                "limit_up": limit_up,
                "technical": technical
            }
        except Exception as e:
            raise Exception(f"Error generating daily review: {str(e)}")
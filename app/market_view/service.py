from typing import List, Dict, Any
from datetime import date
from app.database import engine
import pandas as pd
import numpy as np
from loguru import logger

class MarketReviewService:
    @staticmethod
    def process_float(value: Any) -> float:
        """处理浮点数，将非法值转换为0"""
        try:
            if pd.isna(value) or np.isinf(value):
                return 0.0
            return float(value)
        except:
            return 0.0

    @staticmethod
    def process_dataframe(df: pd.DataFrame) -> List[Dict[str, Any]]:
        """处理 DataFrame，确保所有数值都是 JSON 兼容的"""
        records = df.to_dict('records')
        for record in records:
            for key, value in record.items():
                if isinstance(value, (float, np.float64, np.float32)):
                    record[key] = MarketReviewService.process_float(value)
                elif pd.isna(value):
                    record[key] = None
        return records

    @staticmethod
    async def get_market_overview(trade_date: str) -> Dict[str, Any]:
        """获取市场概览数据"""
        logger.info("Getting market overview data for date: {}", trade_date)
        try:
            # 获取主要指数数据
            index_sql = """
            SELECT 
                ts_code,
                total_mv,
                float_mv,
                total_share,
                float_share,
                free_share,
                turnover_rate,
                turnover_rate_f,
                pe,
                pe_ttm,
                pb
            FROM index_dailybasic
            WHERE trade_date = %(trade_date)s 
            AND ts_code IN (
                '000001.SH',  -- 上证指数
                '399001.SZ',  -- 深证成指
                '399006.SZ',  -- 创业板指
                '000016.SH',  -- 上证50
                '000905.SH',  -- 中证500
                '399005.SZ'   -- 中小板指
            )
            """
            
            df = pd.read_sql(index_sql, engine, params={'trade_date': trade_date})
            
            if df.empty:
                logger.warning("No market data found for date: {}", trade_date)
                return {
                    "indices": [],
                    "upCount": 0,
                    "downCount": 0,
                    "totalAmount": 0
                }
            
            # 处理指数
            indices = []
            for _, row in df.iterrows():
                index_data = {
                    "code": row['ts_code'],
                    "name": {
                        '000001.SH': '上证指数',
                        '399001.SZ': '深证成指',
                        '399006.SZ': '创业板指',
                        '000016.SH': '上证50',
                        '000905.SH': '中证500',
                        '399005.SZ': '中小板指'
                    }.get(row['ts_code'], row['ts_code']),
                    "totalMv": float(row['total_mv'] / 100000000),  # 转换为亿元
                    "floatMv": float(row['float_mv'] / 100000000),  # 转换为亿元
                    "turnoverRate": float(row['turnover_rate']),
                    "turnoverRateF": float(row['turnover_rate_f']),
                    "pe": float(row['pe']),
                    "peTtm": float(row['pe_ttm']),
                    "pb": float(row['pb'])
                }
                indices.append(index_data)
            
            # 获取上涨下跌家数和成交额（从 stock_daily 表）
            stock_sql = """
            SELECT 
                COUNT(CASE WHEN pct_chg > 0 THEN 1 END) as up_count,
                COUNT(CASE WHEN pct_chg < 0 THEN 1 END) as down_count,
                SUM(amount) / 100000 as total_amount  -- amount单位是千元，除以100000转换为亿元
            FROM stock_daily
            WHERE trade_date = %(trade_date)s
            AND (
                ts_code LIKE %(code_prefix_1)s 
                OR ts_code LIKE %(code_prefix_2)s 
                OR ts_code LIKE %(code_prefix_3)s
            )
            """
            stock_params = {
                'trade_date': trade_date,
                'code_prefix_1': '60%',  # 上海主板
                'code_prefix_2': '00%',  # 深圳主板
                'code_prefix_3': '30%'   # 创业板
            }
            
            stock_df = pd.read_sql(stock_sql, engine, params=stock_params)
            
            result = {
                "indices": indices,
                "upCount": int(stock_df['up_count'].iloc[0]),
                "downCount": int(stock_df['down_count'].iloc[0]),
                "totalAmount": float(stock_df['total_amount'].iloc[0])  # 已经在SQL中转换为亿元
            }
            
            logger.debug("Processed data: {}", result)
            return result
        except Exception as e:
            logger.error("Error getting market overview: {}", str(e))
            raise

    @staticmethod
    async def get_sector_flow(trade_date: str) -> List[Dict[str, Any]]:
        """获取板块资金流向"""
        logger.info("Getting sector flow data for date: {}", trade_date)
        try:
            sql = """
            SELECT 
                trade_date,
                ts_code,
                name,
                pct_change,
                close,
                net_amount,
                net_amount_rate,
                buy_elg_amount,
                buy_elg_amount_rate,
                buy_lg_amount,
                buy_lg_amount_rate,
                buy_md_amount,
                buy_md_amount_rate,
                buy_sm_amount,
                buy_sm_amount_rate,
                buy_sm_amount_stock,
                rank
            FROM moneyflow_ind_dc
            WHERE trade_date = %(trade_date)s
            ORDER BY net_amount DESC
            """
            logger.debug("Executing SQL: {}", sql)
            logger.debug("Parameters: {{'trade_date': {}}}", trade_date)
            
            df = pd.read_sql(sql, engine, params={'trade_date': trade_date})
            logger.debug("Query result shape: {}", df.shape)
            if df.empty:
                logger.warning("No sector flow data found for date: {}", trade_date)
                return []
            
            # 处理数据，确保所有值都 JSON 兼容的，并转换金额单位为亿元
            result = []
            for _, row in df.iterrows():
                processed_row = {
                    "tsCode": row['ts_code'],
                    "name": row['name'],
                    "close": float(row['close']) if pd.notnull(row['close']) else 0.0,
                    "pctChange": float(row['pct_change']) if pd.notnull(row['pct_change']) else 0.0,
                    "netAmount": float(row['net_amount'] / 100000000) if pd.notnull(row['net_amount']) else 0.0,  # 转换为亿元
                    "netAmountRate": float(row['net_amount_rate']) if pd.notnull(row['net_amount_rate']) else 0.0,
                    "buyElgAmount": float(row['buy_elg_amount'] / 100000000) if pd.notnull(row['buy_elg_amount']) else 0.0,
                    "buyElgAmountRate": float(row['buy_elg_amount_rate']) if pd.notnull(row['buy_elg_amount_rate']) else 0.0,
                    "buyLgAmount": float(row['buy_lg_amount'] / 100000000) if pd.notnull(row['buy_lg_amount']) else 0.0,
                    "buyLgAmountRate": float(row['buy_lg_amount_rate']) if pd.notnull(row['buy_lg_amount_rate']) else 0.0,
                    "buyMdAmount": float(row['buy_md_amount'] / 100000000) if pd.notnull(row['buy_md_amount']) else 0.0,
                    "buyMdAmountRate": float(row['buy_md_amount_rate']) if pd.notnull(row['buy_md_amount_rate']) else 0.0,
                    "buySmAmount": float(row['buy_sm_amount'] / 100000000) if pd.notnull(row['buy_sm_amount']) else 0.0,
                    "buySmAmountRate": float(row['buy_sm_amount_rate']) if pd.notnull(row['buy_sm_amount_rate']) else 0.0,
                    "hotStock": row['buy_sm_amount_stock'] if pd.notnull(row['buy_sm_amount_stock']) else "",
                    "rank": int(row['rank']) if pd.notnull(row['rank']) else 0
                }
                result.append(processed_row)
            
            logger.debug("Processed data: {}", result)
            return result
        except Exception as e:
            logger.error("Error getting sector flow: {}", str(e))
            raise

    @staticmethod
    async def get_top_list(trade_date: str) -> List[Dict[str, Any]]:
        """获取龙虎榜数据"""
        logger.info("Getting top list data for date: {}", trade_date)
        try:
            # 1. 先获取基础数据
            base_sql = """
            SELECT 
                ts_code,
                name,
                close,
                pct_change,
                turnover_rate,
                amount,
                reason,
                net_rate,
                net_amount
            FROM top_list 
            WHERE trade_date = %(trade_date)s
            """
            
            # 2. 获取机构交易数据
            inst_sql = """
            SELECT 
                ts_code,
                side,
                exalter,
                buy,
                sell,
                buy_rate,
                sell_rate,
                net_buy
            FROM top_inst
            WHERE trade_date = %(trade_date)s
            ORDER BY CASE 
                WHEN side = 0 THEN buy 
                ELSE sell 
            END DESC
            """
            
            params = {'trade_date': trade_date}
            logger.debug("Executing SQL queries")
            
            # 执行查询
            df_base = pd.read_sql(base_sql, engine, params=params)
            df_inst = pd.read_sql(inst_sql, engine, params=params)
            
            if df_base.empty:
                logger.warning("No top list data found for date: {}", trade_date)
                return []
            
            # 处理数据
            result = []
            for _, row in df_base.iterrows():
                try:
                    # 获取该股票的机构交易数据
                    stock_inst = df_inst[df_inst['ts_code'] == row['ts_code']]
                    
                    # 处理买入机构
                    buy_insts = stock_inst[stock_inst['side'] == 0]
                    buy_inst_list = [
                        f"{inst['exalter']}({round(inst['buy_rate']*100, 2)}%)"
                        for _, inst in buy_insts.iterrows()
                    ] if not buy_insts.empty else []
                    
                    # 处理卖出机构
                    sell_insts = stock_inst[stock_inst['side'] == 1]
                    sell_inst_list = [
                        f"{inst['exalter']}({round(inst['sell_rate']*100, 2)}%)"
                        for _, inst in sell_insts.iterrows()
                    ] if not sell_insts.empty else []
                    
                    # 计算汇总数据
                    buy_amount = buy_insts['buy'].sum() if not buy_insts.empty else 0
                    sell_amount = sell_insts['sell'].sum() if not sell_insts.empty else 0
                    net_buy_amount = stock_inst['net_buy'].sum() if not stock_inst.empty else 0
                    
                    processed_row = {
                        "tsCode": str(row['ts_code']),
                        "name": str(row['name']) if pd.notnull(row['name']) else "",
                        "close": float(row['close']) if pd.notnull(row['close']) else 0.0,
                        "change": float(row['pct_change']) if pd.notnull(row['pct_change']) else 0.0,
                        "turnoverRate": float(row['turnover_rate']) if pd.notnull(row['turnover_rate']) else 0.0,
                        "amount": float(row['amount'] / 100000000) if pd.notnull(row['amount']) else 0.0,
                        "reason": str(row['reason']) if pd.notnull(row['reason']) else "",
                        "buyAmount": float(buy_amount / 100000000),
                        "sellAmount": float(sell_amount / 100000000),
                        "netBuyAmount": float(net_buy_amount / 100000000),
                        "buyInst": buy_inst_list,
                        "sellInst": sell_inst_list,
                        "netRate": float(row['net_rate']) if pd.notnull(row['net_rate']) else 0.0,
                        "netAmount": float(row['net_amount'] / 100000000) if pd.notnull(row['net_amount']) else 0.0,
                        "totalTurnover": float(row['amount'] / 100000000) if pd.notnull(row['amount']) else 0.0
                    }
                    result.append(processed_row)
                    logger.debug("Successfully processed row {}", _)
                except Exception as e:
                    logger.error("Error processing row {}: {}", _, str(e))
                    logger.error("Problematic row data: {}", row)
                    continue
            
            logger.debug("Successfully processed {} records", len(result))
            return result
            
        except Exception as e:
            logger.error("Error getting top list: {}", str(e))
            logger.error("Full traceback:", exc_info=True)
            raise

    @staticmethod
    async def get_limit_up(trade_date: str) -> List[Dict[str, Any]]:
        """获取涨停板数据"""
        logger.info("Getting limit up data for date: {}", trade_date)
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
            logger.debug("Executing SQL: {}", sql)
            logger.debug("Parameters: {}", {'trade_date': trade_date})
            
            df = pd.read_sql(sql, engine, params={'trade_date': trade_date})
            logger.debug("Query result shape: {}", df.shape)
            
            if df.empty:
                logger.warning("No limit up data found for date: {}", trade_date)
                return []
            
            # 处理数据
            result = []
            for _, row in df.iterrows():
                try:
                    processed_row = {
                        "stockCode": str(row['ts_code']),
                        "stockName": str(row['name']) if pd.notnull(row['name']) else "",
                        "limitUpTime": str(row['lu_time']) if pd.notnull(row['lu_time']) else "",
                        "limitUpReason": str(row['lu_desc']) if pd.notnull(row['lu_desc']) else "",
                        "turnoverRate": float(row['turnover_rate']) if pd.notnull(row['turnover_rate']) else 0.0,
                        "amount": float(row['amount']) if pd.notnull(row['amount']) else 0.0,
                        "status": str(row['status']) if pd.notnull(row['status']) else "",
                        "theme": str(row['theme']) if pd.notnull(row['theme']) else "",
                        "netChange": float(row['net_change']) if pd.notnull(row['net_change']) else 0.0,
                        "bidAmount": float(row['bid_amount']) if pd.notnull(row['bid_amount']) else 0.0,
                        "bidTurnover": float(row['bid_turnover']) if pd.notnull(row['bid_turnover']) else 0.0,
                        "freeFloat": float(row['free_float']) if pd.notnull(row['free_float']) else 0.0
                    }
                    result.append(processed_row)
                    logger.debug("Successfully processed limit up row")
                except Exception as e:
                    logger.error("Error processing limit up row: {}", str(e))
                    logger.error("Problematic row: {}", row)
                    continue
            
            logger.debug("Successfully processed {} limit up stocks", len(result))
            return result
        except Exception as e:
            logger.error("Error getting limit up data: {}", str(e))
            logger.error("Full traceback:", exc_info=True)
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
        logger.info("Getting concept data for date: {}", trade_date)
        try:
            # 1. 先获取基础概念数据
            base_sql = """
            SELECT 
                ts_code,
                name,
                z_t_num,
                up_num
            FROM kpl_concept
            WHERE trade_date = %(trade_date)s
            """
            
            logger.debug("Executing base SQL: {}", base_sql)
            logger.debug("With parameters: {}", {'trade_date': trade_date})
            
            # 先测试基础查询是否正常
            df_base = pd.read_sql(base_sql, engine, params={'trade_date': trade_date})
            logger.debug("Base query result shape: {}", df_base.shape)
            
            if df_base.empty:
                logger.warning("No concept data found for date: {}", trade_date)
                return []
            
            # 2. 如果基础查询成功，再获取成分股数据
            cons_sql = """
            SELECT 
                ts_code,
                COUNT(cons_code) as stock_count,
                STRING_AGG(cons_name, ',') as cons_list,
                MAX(hot_num) as hot_num,
                MAX(description) as description
            FROM kpl_concept_cons
            WHERE trade_date = %(trade_date)s
            GROUP BY ts_code
            """
            
            logger.debug("Executing cons SQL: {}", cons_sql)
            df_cons = pd.read_sql(cons_sql, engine, params={'trade_date': trade_date})
            logger.debug("Cons query result shape: {}", df_cons.shape)
            
            # 3. 合并数据
            df = pd.merge(df_base, df_cons, on='ts_code', how='left')
            logger.debug("Merged DataFrame shape: {}", df.shape)
            
            # 4. 处理数据
            result = []
            for _, row in df.iterrows():
                try:
                    processed_row = {
                        "tsCode": str(row['ts_code']),
                        "conceptName": str(row['name']),
                        "stockCount": int(row['stock_count']) if pd.notnull(row['stock_count']) else 0,
                        "limitUpCount": int(row['z_t_num']) if pd.notnull(row['z_t_num']) else 0,
                        "upCount": int(row['up_num']) if pd.notnull(row['up_num']) else 0,
                        "leadingStocks": str(row['cons_list']).split(',') if pd.notnull(row['cons_list']) else [],
                        "hotNum": int(row['hot_num']) if pd.notnull(row['hot_num']) else 0,
                        "description": str(row['description']) if pd.notnull(row['description']) else ""
                    }
                    result.append(processed_row)
                    logger.debug("Successfully processed concept row")
                except Exception as e:
                    logger.error("Error processing concept row: {}", str(e))
                    logger.error("Problematic row: {}", row.to_dict())
                    continue
            
            # 5. 排序并限制返回数量
            result.sort(key=lambda x: (-x['limitUpCount'], -x['upCount']))
            result = result[:30]
            
            logger.debug("Successfully processed {} concepts", len(result))
            return result
            
        except Exception as e:
            logger.error("Error getting concept data: {}", str(e))
            logger.error("Full traceback:", exc_info=True)
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

    @staticmethod
    async def get_concept_stocks(trade_date: str, concept_name: str) -> List[Dict[str, Any]]:
        """获取概念成分股数据"""
        logger.info("Getting concept stocks for date: {} concept: {}", trade_date, concept_name)
        try:
            # 1. 先获取概念的 ts_code
            concept_sql = """
            SELECT ts_code
            FROM kpl_concept
            WHERE trade_date = %(trade_date)s AND name = %(concept_name)s
            LIMIT 1
            """
            
            params = {
                'trade_date': trade_date,
                'concept_name': concept_name
            }
            
            # 获取概念代码
            df_concept = pd.read_sql(concept_sql, engine, params=params)
            if df_concept.empty:
                logger.warning("No concept found for name: {}", concept_name)
                return []
            
            concept_code = df_concept['ts_code'].iloc[0]
            logger.debug("Found concept code: {}", concept_code)
            
            # 2. 使用概念代码查询成分股
            stocks_sql = """
            WITH concept_stocks AS (
                SELECT cons_code
                FROM kpl_concept_cons
                WHERE trade_date = %(trade_date)s AND ts_code = %(concept_code)s
            )
            SELECT 
                l.*
            FROM kpl_list l
            JOIN concept_stocks cs ON l.ts_code = cs.cons_code
            WHERE l.trade_date = %(trade_date)s
            ORDER BY l.pct_chg DESC
            """
            
            params = {
                'trade_date': trade_date,
                'concept_code': concept_code
            }
            
            df = pd.read_sql(stocks_sql, engine, params=params)
            logger.debug("Found {} stocks for concept", len(df))
            
            if df.empty:
                return []
            
            result = []
            for _, row in df.iterrows():
                processed_row = {
                    "ts_code": str(row['ts_code']),
                    "name": str(row['name']) if pd.notnull(row['name']) else "",
                    "pct_chg": float(row['pct_chg']) if pd.notnull(row['pct_chg']) else 0.0,
                    "amount": float(row['amount']) if pd.notnull(row['amount']) else 0.0,
                    "turnover_rate": float(row['turnover_rate']) if pd.notnull(row['turnover_rate']) else 0.0,
                    "status": str(row['status']) if pd.notnull(row['status']) else "",
                    "lu_time": str(row['lu_time']) if pd.notnull(row['lu_time']) else "",
                    "lu_desc": str(row['lu_desc']) if pd.notnull(row['lu_desc']) else ""
                }
                result.append(processed_row)
            
            return result
            
        except Exception as e:
            logger.error("Error getting concept stocks: {}", str(e))
            logger.error("Full traceback:", exc_info=True)
            raise
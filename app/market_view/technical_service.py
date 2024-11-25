from typing import List, Dict, Any
from datetime import date
from app.database import engine
import pandas as pd
import numpy as np
from loguru import logger

class TechnicalAnalysisService:
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
    async def get_technical_indicators(ts_code: str, trade_date: str) -> Dict[str, Any]:
        """获取股票技术指标数据"""
        logger.info(f"Getting technical indicators for stock: {ts_code}, date: {trade_date}")
        try:
            sql = """
            SELECT 
                -- 趋势指标
                ma_bfq_5, ma_bfq_10, ma_bfq_20, ma_bfq_60,
                macd_bfq, macd_dif_bfq, macd_dea_bfq,
                boll_upper_bfq, boll_mid_bfq, boll_lower_bfq,
                -- KDJ指标
                kdj_k_bfq, kdj_d_bfq, kdj_bfq,
                -- RSI指标
                rsi_bfq_6, rsi_bfq_12, rsi_bfq_24,
                -- 成交量指标
                vol, amount, turnover_rate, turnover_rate_f,
                -- 波动指标
                atr_bfq,
                bias1_bfq, bias2_bfq, bias3_bfq,
                -- 其他基础数据
                open, high, low, close,
                pct_chg
            FROM stk_factor_pro
            WHERE ts_code = %(ts_code)s 
            AND trade_date = %(trade_date)s
            """
            
            df = pd.read_sql(sql, engine, params={
                'ts_code': ts_code,
                'trade_date': trade_date
            })
            
            if df.empty:
                logger.warning(f"No technical data found for stock {ts_code} on date {trade_date}")
                return {}
            
            # 处理数据
            result = df.iloc[0].to_dict()
            
            # 计算趋势状态
            ma5 = result['ma_bfq_5']
            ma10 = result['ma_bfq_10']
            ma20 = result['ma_bfq_20']
            ma60 = result['ma_bfq_60']
            close = result['close']
            
            trend = {
                'short_term': 'up' if close > ma5 else 'down',
                'medium_term': 'up' if close > ma20 else 'down',
                'long_term': 'up' if close > ma60 else 'down',
                'ma_cross': {
                    'golden_cross': ma5 > ma10 and ma10 > ma20,
                    'death_cross': ma5 < ma10 and ma10 < ma20
                }
            }
            
            # 计算MACD信号
            macd_signal = {
                'trend': 'up' if result['macd_bfq'] > 0 else 'down',
                'divergence': result['macd_dif_bfq'] - result['macd_dea_bfq']
            }
            
            # 汇总分析结果
            analysis = {
                'trend': trend,
                'macd': macd_signal,
                'kdj': {
                    'k': result['kdj_k_bfq'],
                    'd': result['kdj_d_bfq'],
                    'j': result['kdj_bfq'],
                    'signal': 'overbought' if result['kdj_bfq'] > 80 else 'oversold' if result['kdj_bfq'] < 20 else 'neutral'
                },
                'rsi': {
                    'rsi6': result['rsi_bfq_6'],
                    'rsi12': result['rsi_bfq_12'],
                    'rsi24': result['rsi_bfq_24']
                },
                'volatility': {
                    'atr': result['atr_bfq'],
                    'bias1': result['bias1_bfq'],
                    'bias2': result['bias2_bfq'],
                    'bias3': result['bias3_bfq']
                },
                'price': {
                    'open': result['open'],
                    'high': result['high'],
                    'low': result['low'],
                    'close': result['close'],
                    'change_pct': result['pct_chg']
                }
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error getting technical indicators: {str(e)}")
            raise

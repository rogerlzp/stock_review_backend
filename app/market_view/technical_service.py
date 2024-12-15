from typing import List, Dict, Any
from datetime import date
from app.core.database import engine
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
    async def get_technical_indicators(
        ts_code: str, 
        end_date: str = None,
        period: int = 90
    ) -> Dict[str, Any]:
        """获取股票技术指标数据
        
        Args:
            ts_code: 股票代码
            end_date: 结束日期，默认为最新交易日
            period: 获取天数，默认90天
        """
        logger.info(f"Getting technical indicators for stock: {ts_code}, period: {period} days")
        try:
            # 如果未指定结束日期，获取最新交易日
            if not end_date:
                latest_date_sql = """
                SELECT MAX(trade_date) as latest_date 
                FROM stk_factor_pro 
                WHERE ts_code = %(ts_code)s
                """
                latest_date_df = pd.read_sql(latest_date_sql, engine, params={'ts_code': ts_code})
                end_date = latest_date_df['latest_date'].iloc[0]

            sql = """
            WITH date_range AS (
                SELECT trade_date
                FROM stk_factor_pro
                WHERE ts_code = %(ts_code)s
                AND trade_date <= %(end_date)s
                ORDER BY trade_date DESC
                LIMIT %(period)s
            )
            SELECT 
                trade_date,
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
            AND trade_date IN (SELECT trade_date FROM date_range)
            ORDER BY trade_date ASC
            """
            
            df = pd.read_sql(sql, engine, params={
                'ts_code': ts_code,
                'end_date': end_date,
                'period': period
            })
            
            if df.empty:
                logger.warning(f"No technical data found for stock {ts_code}")
                return {}
            
            # 将日期列转换为字符串格式
            df['trade_date'] = df['trade_date'].astype(str)
            
            # 处理每一天的技术指标
            daily_analysis = []
            for _, row in df.iterrows():
                analysis = {
                    'trade_date': row['trade_date'],
                    'trend': {
                        'short_term': 'up' if row['close'] > row['ma_bfq_5'] else 'down',
                        'medium_term': 'up' if row['close'] > row['ma_bfq_20'] else 'down',
                        'long_term': 'up' if row['close'] > row['ma_bfq_60'] else 'down',
                        'ma_cross': {
                            'golden_cross': row['ma_bfq_5'] > row['ma_bfq_10'] and row['ma_bfq_10'] > row['ma_bfq_20'],
                            'death_cross': row['ma_bfq_5'] < row['ma_bfq_10'] and row['ma_bfq_10'] < row['ma_bfq_20']
                        }
                    },
                    'macd': {
                        'trend': 'up' if row['macd_bfq'] > 0 else 'down',
                        'divergence': row['macd_dif_bfq'] - row['macd_dea_bfq'],
                        'macd': row['macd_bfq'],
                        'dif': row['macd_dif_bfq'],
                        'dea': row['macd_dea_bfq']
                    },
                    'kdj': {
                        'k': row['kdj_k_bfq'],
                        'd': row['kdj_d_bfq'],
                        'j': row['kdj_bfq'],
                        'signal': 'overbought' if row['kdj_bfq'] > 80 else 'oversold' if row['kdj_bfq'] < 20 else 'neutral'
                    },
                    'rsi': {
                        'rsi6': row['rsi_bfq_6'],
                        'rsi12': row['rsi_bfq_12'],
                        'rsi24': row['rsi_bfq_24']
                    },
                    'volatility': {
                        'atr': row['atr_bfq'],
                        'bias1': row['bias1_bfq'],
                        'bias2': row['bias2_bfq'],
                        'bias3': row['bias3_bfq']
                    },
                    'price': {
                        'open': row['open'],
                        'high': row['high'],
                        'low': row['low'],
                        'close': row['close'],
                        'change_pct': row['pct_chg']
                    },
                    'volume': {
                        'volume': row['vol'],
                        'amount': row['amount'],
                        'turnover_rate': row['turnover_rate'],
                        'turnover_rate_free': row['turnover_rate_f']
                    }
                }
                daily_analysis.append(analysis)
            
            return {
                'ts_code': ts_code,
                'period': period,
                'start_date': daily_analysis[0]['trade_date'],
                'end_date': daily_analysis[-1]['trade_date'],
                'data': daily_analysis
            }
            
        except Exception as e:
            logger.error(f"Error getting technical indicators: {str(e)}")
            raise

from typing import List
from sqlalchemy.orm import Session
from app.core.database import get_db
from loguru import logger

logger = logger.bind(module=__name__)

class StockVolumePriceService:
    def __init__(self, db: Session = None):
        self.db = next(get_db()) if db is None else db
    
    async def get_stock_volume_price_analysis(self, ts_codes: List[str], trade_date: str):
        """获取指定股票的量价分析"""
        try:
            # 1. 获取基础量价数据
            basic_data = await self._get_basic_data(ts_codes, trade_date)
            if not basic_data:
                return []
            
            # 2. 获取资金流向数据
            flow_data = await self._get_money_flow(ts_codes, trade_date)
            
            # 3. 获取技术指标数据
            tech_data = await self._get_technical_data(ts_codes, trade_date)
            
            # 4. 分析每只股票的异常情况
            result = []
            for ts_code in ts_codes:
                if ts_code not in basic_data:
                    continue
                    
                stock_result = {
                    "ts_code": ts_code,
                    "anomalies": self._analyze_single_stock(
                        basic_data.get(ts_code),
                        flow_data.get(ts_code),
                        tech_data.get(ts_code)
                    ),
                    "details": {
                        "basic": basic_data.get(ts_code),
                        "flow": flow_data.get(ts_code),
                        "technical": tech_data.get(ts_code)
                    }
                }
                result.append(stock_result)
            
            return result
        except Exception as e:
            logger.error(f"Error in get_stock_volume_price_analysis: {str(e)}")
            raise

    async def _get_basic_data(self, ts_codes: List[str], trade_date: str):
        """获取基础量价数据（包括历史数据用于对比）"""
        query = """
        WITH hist_data AS (
            SELECT 
                ts_code,
                trade_date,
                close,
                vol,
                amount,
                pct_chg,
                LAG(vol, 1) OVER (PARTITION BY ts_code ORDER BY trade_date) as pre_vol,
                LAG(amount, 1) OVER (PARTITION BY ts_code ORDER BY trade_date) as pre_amount,
                AVG(vol) OVER (PARTITION BY ts_code ORDER BY trade_date ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING) as avg_vol_5d
            FROM stock_daily
            WHERE ts_code = ANY(:ts_codes)
            AND trade_date <= :trade_date
            ORDER BY trade_date DESC
        )
        SELECT * FROM hist_data WHERE trade_date = :trade_date
        """
        result = await self.db.fetch_all(query, {"ts_codes": ts_codes, "trade_date": trade_date})
        return {row['ts_code']: row for row in result} if result else {}

    async def _get_money_flow(self, ts_codes: List[str], trade_date: str):
        """获取资金流向数据"""
        query = """
        SELECT * FROM moneyflow_dc
        WHERE ts_code = ANY(:ts_codes)
        AND trade_date = :trade_date
        """
        result = await self.db.fetch_all(query, {"ts_codes": ts_codes, "trade_date": trade_date})
        return {row['ts_code']: row for row in result} if result else {}

    async def _get_technical_data(self, ts_codes: List[str], trade_date: str):
        """获取技术指标数据"""
        query = """
        SELECT 
            ts_code,
            volume_ratio,
            mfi_qfq,
            rsi_qfq_6,
            macd_qfq,
            kdj_k_qfq,
            kdj_d_qfq,
            kdj_j_qfq
        FROM stock_factor_pro
        WHERE ts_code = ANY(:ts_codes)
        AND trade_date = :trade_date
        """
        result = await self.db.fetch_all(query, {"ts_codes": ts_codes, "trade_date": trade_date})
        return {row['ts_code']: row for row in result} if result else {}

    def _analyze_single_stock(self, basic_data, flow_data, tech_data):
        """分析单个股票的异常情况"""
        if not all([basic_data, flow_data, tech_data]):
            return []
            
        anomalies = []
        
        # 1. 检查量价背离
        if basic_data['pct_chg'] > 2 and basic_data['vol'] < basic_data['pre_vol'] * 0.8:
            anomalies.append({
                "type": "price_up_volume_down",
                "description": "价格上涨但成交量萎缩",
                "severity": "medium",
                "indicators": {
                    "price_change": basic_data['pct_chg'],
                    "volume_ratio": basic_data['vol'] / basic_data['pre_vol']
                }
            })
        
        # 2. 检查资金流向异常
        if flow_data['net_amount'] < -1000 and abs(flow_data['net_amount_rate']) > 30:
            anomalies.append({
                "type": "main_force_outflow",
                "description": "主力资金大幅流出",
                "severity": "high",
                "indicators": {
                    "net_amount": flow_data['net_amount'],
                    "net_amount_rate": flow_data['net_amount_rate']
                }
            })
        
        # 3. 检查技术指标异常
        if tech_data['mfi_qfq'] < 20 or tech_data['mfi_qfq'] > 80:
            anomalies.append({
                "type": "mfi_extreme",
                "description": "资金流量指标处于极值",
                "severity": "medium",
                "indicators": {
                    "mfi": tech_data['mfi_qfq']
                }
            })

        return anomalies

    async def get_stock_info(self, code: str, date: str):
        """获取股票基本信息"""
        try:
            # 将YYYY-MM-DD格式转换为YYYYMMDD
            trade_date = date.replace('-', '')
            
            # 从数据库获取股票基本信息
            query = f"""
                SELECT
                    ts_code,
                    name,
                    close as current_price,
                    change as price_change,
                    pct_chg as change_percent,
                    turnover_rate
                FROM daily_basic
                WHERE ts_code = '{code}'
                AND trade_date = '{trade_date}'
            """
            result = await self.db.execute(query)
            stock_info = result.fetchone()
            
            if not stock_info:
                return None
                
            return {
                "code": stock_info.ts_code,
                "name": stock_info.name,
                "currentPrice": stock_info.current_price,
                "priceChange": stock_info.price_change,
                "changePercent": stock_info.change_percent,
                "turnoverRate": stock_info.turnover_rate
            }
        except Exception as e:
            logger.error(f"Error in get_stock_info: {str(e)}")
            raise

    async def get_stock_volume_price_data(self, code: str, date: str):
        """获取个股量价数据"""
        try:
            # 将YYYY-MM-DD格式转换为YYYYMMDD
            end_date = date.replace('-', '')
            
            # 获取前60个交易日的数据
            query = f"""
                SELECT
                    trade_date,
                    open,
                    high,
                    low,
                    close,
                    vol as volume,
                    amount
                FROM stock_daily
                WHERE ts_code = '{code}'
                AND trade_date <= '{end_date}'
                ORDER BY trade_date DESC
                LIMIT 60
            """
            result = await self.db.execute(query)
            daily_data = result.fetchall()
            
            if not daily_data:
                return None
            
            # 计算均量
            volumes = [row.volume for row in daily_data]
            avg_volume_5 = sum(volumes[:5]) / 5 if len(volumes) >= 5 else None
            avg_volume_10 = sum(volumes[:10]) / 10 if len(volumes) >= 10 else None
            avg_volume_20 = sum(volumes[:20]) / 20 if len(volumes) >= 20 else None
            
            # 计算量比
            volume_ratio = volumes[0] / avg_volume_5 if avg_volume_5 else None
            
            # 构建K线数据
            dates = []
            kline_data = []
            volumes_data = []
            
            for row in reversed(daily_data):
                dates.append(row.trade_date)
                kline_data.append([
                    float(row.open),
                    float(row.close),
                    float(row.low),
                    float(row.high)
                ])
                volumes_data.append(float(row.volume))
            
            return {
                "dates": dates,
                "klineData": kline_data,
                "volumes": volumes_data,
                "volume": float(volumes[0]),
                "amount": float(daily_data[0].amount),
                "volumeRatio": volume_ratio,
                "avgVolume5": float(avg_volume_5) if avg_volume_5 else None,
                "avgVolume10": float(avg_volume_10) if avg_volume_10 else None,
                "avgVolume20": float(avg_volume_20) if avg_volume_20 else None
            }
        except Exception as e:
            logger.error(f"Error in get_stock_volume_price_data: {str(e)}")
            raise

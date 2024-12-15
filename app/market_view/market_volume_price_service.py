from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db
from loguru import logger

logger = logger.bind(module=__name__)

class MarketVolumePriceService:
    def __init__(self, db: Session = None):
        self.db = next(get_db()) if db is None else db
    
    def get_market_volume_data(self, trade_date: str):
        """获取市场量价数据"""
        logger.info("Getting market volume data for date: {}", trade_date)
        try:
            # 将YYYY-MM-DD格式转换为YYYYMMDD
            formatted_date = trade_date.replace('-', '')
            logger.debug("Formatted date: {}", formatted_date)
            
            # 先检查一些样本数据
            debug_query = text("""
                WITH volume_stats AS (
                    SELECT 
                        d.ts_code,
                        s.name,
                        d.vol,
                        d.amount,
                        AVG(d.vol) OVER (PARTITION BY d.ts_code ORDER BY d.trade_date DESC ROWS BETWEEN 1 FOLLOWING AND 5 FOLLOWING) as avg_vol_5
                    FROM stock_daily d
                    JOIN stock_basic s ON d.ts_code = s.ts_code
                    WHERE d.trade_date = :trade_date
                )
                SELECT 
                    ts_code,
                    name,
                    vol,
                    avg_vol_5,
                    CASE 
                        WHEN vol = 0 OR avg_vol_5 = 0 THEN 0 
                        ELSE vol::float / NULLIF(avg_vol_5, 0) 
                    END as volume_ratio
                FROM volume_stats
                WHERE vol > 0 AND avg_vol_5 > 0
                ORDER BY volume_ratio DESC
                LIMIT 10
            """)
            debug_result = self.db.execute(debug_query, {"trade_date": formatted_date})
            debug_data = debug_result.fetchall()
            logger.info("Sample data for debugging:")
            for row in debug_data:
                logger.info("Stock: {}, Name: {}, Volume: {}, Avg5: {}, Ratio: {:.2f}", 
                          row.ts_code, row.name, row.vol, row.avg_vol_5, row.volume_ratio)

            # 获取市场总成交量和成交额
            logger.debug("Querying total market volume and amount")
            query = text("""
                WITH daily_stats AS (
                    SELECT 
                        trade_date,
                        SUM(vol * 100) as total_volume,
                        SUM(amount) as total_amount
                    FROM stock_daily
                    WHERE trade_date <= :trade_date
                    GROUP BY trade_date
                    ORDER BY trade_date DESC
                    LIMIT 20
                )
                SELECT 
                    total_volume,
                    total_amount
                FROM daily_stats
                ORDER BY trade_date DESC
            """)
            result = self.db.execute(query, {"trade_date": formatted_date})
            market_data = result.fetchone()
            logger.debug("Market data: total_volume={}, total_amount={}", 
                        market_data.total_volume, market_data.total_amount)
            
            # 获取前20个交易日的数据计算均量
            logger.debug("Querying historical volume data for averages")
            query = text("""
                SELECT
                    trade_date,
                    SUM(vol) as total_volume
                FROM stock_daily
                WHERE trade_date <= :trade_date
                GROUP BY trade_date
                ORDER BY trade_date DESC
                LIMIT 20
            """)
            result = self.db.execute(query, {"trade_date": formatted_date})
            daily_data = result.fetchall()
            
            volumes = [row.total_volume for row in daily_data]
            avg_volume_5 = sum(volumes[:5]) / 5 if len(volumes) >= 5 else None
            avg_volume_10 = sum(volumes[:10]) / 10 if len(volumes) >= 10 else None
            avg_volume_20 = sum(volumes[:20]) / 20 if len(volumes) >= 20 else None
            logger.debug("Calculated averages: 5d={}, 10d={}, 20d={}", 
                        avg_volume_5, avg_volume_10, avg_volume_20)
            
            # 计算量比
            volume_ratio = volumes[0] / avg_volume_5 if avg_volume_5 else None
            logger.debug("Volume ratio: {}", volume_ratio)
            
            # 确保 volume_condition 有默认值
            if 'volume_condition' not in locals():
                volume_condition = 'volume_ratio_5 >= 1.5'  # 默认使用5日均量比率

            logger.debug("Using volume condition: {}", volume_condition)
            query = text("""
                WITH base_stats AS (
                    SELECT
                        d.ts_code,
                        d.vol * 100 as volume,
                        d.close,
                        d.pct_chg,
                        d.amount,
                        s.name,
                        AVG(d.vol * 100) OVER (PARTITION BY d.ts_code ORDER BY d.trade_date DESC ROWS BETWEEN 1 FOLLOWING AND 5 FOLLOWING) as avg_vol_5,
                        AVG(d.vol * 100) OVER (PARTITION BY d.ts_code ORDER BY d.trade_date DESC ROWS BETWEEN 9 FOLLOWING AND 18 FOLLOWING) as avg_vol_10,
                        AVG(d.vol * 100) OVER (PARTITION BY d.ts_code ORDER BY d.trade_date DESC ROWS BETWEEN 19 FOLLOWING AND 38 FOLLOWING) as avg_vol_20,
                        AVG(d.vol * 100) OVER (PARTITION BY d.ts_code ORDER BY d.trade_date DESC ROWS BETWEEN 59 FOLLOWING AND 118 FOLLOWING) as avg_vol_60
                    FROM stock_daily d
                    JOIN stock_basic s ON d.ts_code = s.ts_code
                    WHERE d.trade_date = :trade_date
                ),
                volume_stats AS (
                    SELECT
                        ts_code,
                        name,
                        close,
                        pct_chg,
                        volume,
                        amount,
                        volume / NULLIF(avg_vol_5, 0) as volume_ratio_5,
                        volume / NULLIF(avg_vol_10, 0) as volume_ratio_10,Execution failed for task ':app:processReleaseResources'.
> A failure occurred while executing com.android.build.gradle.internal.res.LinkApplicationAndroidResourcesTask$TaskAction
   > Android resource linking failed
     com.example.martin1e.app-mergeReleaseResources-38:/values/values.xml:245: error: resource attr/colorPrimaryVariant (aka com.example.martin1e:attr/colorPrimaryVariant) not found.
     error: resource style/Theme.MaterialComponents.DayNight.DarkActionBar (aka com.example.martin1e:style/Theme.MaterialComponents.DayNight.DarkActionBar) not found.
     com.example.martin1e.app-mergeReleaseResources-38:/values/values.xml:237: error: style attribute 'attr/colorPrimary (aka com.example.martin1e:attr/colorPrimary)' not found.
     com.example.martin1e.app-mergeReleaseResources-38:/values/values.xml:238: error: style attribute 'attr/colorPrimaryVariant (aka com.example.martin1e:attr/colorPrimaryVariant)' not found.
     com.example.martin1e.app-mergeReleaseResources-38:/values/values.xml:239: error: style attribute 'attr/colorOnPrimary (aka com.example.martin1e:attr/colorOnPrimary)' not found.
     com.example.martin1e.app-mergeReleaseResources-38:/values/values.xml:241: error: style attribute 'attr/colorSecondary (aka com.example.martin1e:attr/colorSecondary)' not found.
     com.example.martin1e.app-mergeReleaseResources-38:/values/values.xml:242: error: style attribute 'attr/colorSecondaryVariant (aka com.example.martin1e:attr/colorSecondaryVariant)' not found.
     com.example.martin1e.app-mergeReleaseResources-38:/values/values.xml:243: error: style attribute 'attr/colorOnSecondary (aka com.example.martin1e:attr/colorOnSecondary)' not found.
     com.example.martin1e.app-mergeReleaseResources-38:/values/values.xml:245: error: resource attr/colorPrimaryVariant (aka com.example.martin1e:attr/colorPrimaryVariant) not found.
     com.example.martin1e.app-mergeReleaseResources-38:/values-night-v8/values-night-v8.xml:13: error: resource attr/colorPrimaryVariant (aka com.example.martin1e:attr/colorPrimaryVariant) not found.
     error: resource style/Theme.MaterialComponents.DayNight.DarkActionBar (aka com.example.martin1e:style/Theme.MaterialComponents.DayNight.DarkActionBar) not found.
     com.example.martin1e.app-mergeReleaseResources-38:/values-night-v8/values-night-v8.xml:5: error: style attribute 'attr/colorPrimary (aka com.example.martin1e:attr/colorPrimary)' not found.
     com.example.martin1e.app-mergeReleaseResources-38:/values-night-v8/values-night-v8.xml:6: error: style attribute 'attr/colorPrimaryVariant (aka com.example.martin1e:attr/colorPrimaryVariant)' not found.
     com.example.martin1e.app-mergeReleaseResources-38:/values-night-v8/values-night-v8.xml:7: error: style attribute 'attr/colorOnPrimary (aka com.example.martin1e:attr/colorOnPrimary)' not found.
     com.example.martin1e.app-mergeReleaseResources-38:/values-night-v8/values-night-v8.xml:9: error: style attribute 'attr/colorSecondary (aka com.example.martin1e:attr/colorSecondary)' not found.
     com.example.martin1e.app-mergeReleaseResources-38:/values-night-v8/values-night-v8.xml:10: error: style attribute 'attr/colorSecondaryVariant (aka com.example.martin1e:attr/colorSecondaryVariant)' not found.
     com.example.martin1e.app-mergeReleaseResources-38:/values-night-v8/values-night-v8.xml:11: error: style attribute 'attr/colorOnSecondary (aka com.example.martin1e:attr/colorOnSecondary)' not found.
     com.example.martin1e.app-mergeReleaseResources-38:/values-night-v8/values-night-v8.xml:13: error: resource attr/colorPrimaryVariant (aka com.example.martin1e:attr/colorPrimaryVariant) not found.
     error: failed linking references.

* Try:
> Run with --stacktrace option to get the stack trace.
> Run with --info or --debug option to get more log output.
> Run with --scan to get full insights.
> Get more help at https://help.gradle.org.
BUILD FAILED in 30s
31 actionable tasks: 31 executed
                        volume / NULLIF(avg_vol_20, 0) as volume_ratio_20,
                        volume / NULLIF(avg_vol_60, 0) as volume_ratio_60
                    FROM base_stats
                )
                SELECT
                    ts_code as code,
                    name,
                    close as price,
                    pct_chg as change_percent,
                    volume,
                    amount,
                    volume_ratio_5,
                    volume_ratio_10,
                    volume_ratio_20,
                    volume_ratio_60
                FROM volume_stats
                WHERE """ + volume_condition + """
                ORDER BY ABS(pct_chg) DESC
                LIMIT 100
            """)
            result = self.db.execute(query, {"trade_date": formatted_date})
            volume_distribution = result.fetchall()
            logger.debug("Volume distribution calculated with {} ranges", len(volume_distribution))
            
            # 计算成交量分布
            logger.debug("Calculating volume distribution")
            volume_distribution_query = text("""
                WITH base_stats AS (
                    SELECT
                        d.ts_code,
                        d.vol * 100 as volume,
                        AVG(d.vol * 100) OVER (PARTITION BY d.ts_code ORDER BY d.trade_date DESC ROWS BETWEEN 4 FOLLOWING AND 8 FOLLOWING) as avg_vol_5
                    FROM stock_daily d
                    WHERE d.trade_date = :trade_date
                ),
                ratios AS (
                    SELECT
                        CASE
                            WHEN avg_vol_5 > 0 AND volume / avg_vol_5 >= 2 THEN '2倍以上'
                            WHEN avg_vol_5 > 0 AND volume / avg_vol_5 >= 1.5 THEN '1.5-2倍'
                            WHEN avg_vol_5 > 0 AND volume / avg_vol_5 >= 1 THEN '1-1.5倍'
                            WHEN avg_vol_5 > 0 AND volume / avg_vol_5 >= 0.5 THEN '0.5-1倍'
                            WHEN avg_vol_5 > 0 THEN '0.5倍以下'
                            ELSE '未分类'
                        END as range
                    FROM base_stats
                    WHERE avg_vol_5 > 0
                ),
                all_ranges AS (
                    SELECT unnest(ARRAY[
                        '0.5倍以下',
                        '0.5-1倍',
                        '1-1.5倍',
                        '1.5-2倍',
                        '2倍以上',
                        '未分类'
                    ]) as range
                )
                SELECT 
                    ar.range,
                    COUNT(r.range) as count
                FROM all_ranges ar
                LEFT JOIN ratios r ON r.range = ar.range
                GROUP BY ar.range
                ORDER BY 
                    CASE ar.range
                        WHEN '0.5倍以下' THEN 1
                        WHEN '0.5-1倍' THEN 2
                        WHEN '1-1.5倍' THEN 3
                        WHEN '1.5-2倍' THEN 4
                        WHEN '2倍以上' THEN 5
                        WHEN '未分类' THEN 6
                    END
            """)
            volume_distribution_result = self.db.execute(volume_distribution_query, {"trade_date": formatted_date})
            volume_distribution = volume_distribution_result.fetchall()

            # 将volumeDistribution添加到返回的数据中
            response_data = {
                "totalVolume": float(market_data.total_volume),
                "totalAmount": float(market_data.total_amount),
                "volumeRatio": volume_ratio,
                "avgVolume5": float(avg_volume_5) if avg_volume_5 else None,
                "avgVolume10": float(avg_volume_10) if avg_volume_10 else None,
                "avgVolume20": float(avg_volume_20) if avg_volume_20 else None,
                "volumeDistribution": [{"range": row.range, "count": row.count} for row in volume_distribution]
            }
            logger.info("Successfully retrieved market volume data for date: {}", trade_date)
            return response_data
        except Exception as e:
            logger.error("Error in get_market_volume_data: {}", str(e))
            raise
    
    def get_anomaly_stocks(self, trade_date: str, type: str):
        """获取异常股票列表"""
        logger.info("Getting anomaly stocks for date: {}, type: {}", trade_date, type)
        try:
            # 将YYYY-MM-DD格式转换为YYYYMMDD
            formatted_date = trade_date.replace('-', '')
            logger.debug("Formatted date: {}", formatted_date)
            
            # 构建SQL查询条件
            volume_conditions = {
                'volume_up': 'volume_ratio >= 1.5 AND pct_chg > 0',
                'volume_down': 'volume_ratio >= 1.5 AND pct_chg < 0',
                'volume_decrease_up': 'volume_ratio <= 0.5 AND pct_chg > 0',
                'volume_decrease_down': 'volume_ratio <= 0.5 AND pct_chg < 0'
            }
            
            volume_condition = volume_conditions.get(type)
            if not volume_condition:
                error_msg = f"Invalid anomaly type: {type}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            logger.debug("Using volume condition: {}", volume_condition)
            query = text("""
                WITH base_stats AS (
                    SELECT
                        d.ts_code,
                        d.vol * 100 as volume,
                        d.close,
                        d.pct_chg,
                        d.amount,
                        s.name,
                        AVG(d.vol * 100) OVER (PARTITION BY d.ts_code ORDER BY d.trade_date DESC ROWS BETWEEN 1 FOLLOWING AND 5 FOLLOWING) as avg_vol_5
                    FROM stock_daily d
                    JOIN stock_basic s ON d.ts_code = s.ts_code
                    WHERE d.trade_date = :trade_date
                ),
                volume_stats AS (
                    SELECT
                        ts_code,
                        name,
                        close,
                        pct_chg,
                        volume,
                        amount,
                        volume / NULLIF(avg_vol_5, 0) as volume_ratio
                    FROM base_stats
                )
                SELECT
                    ts_code as code,
                    name,
                    close as price,
                    pct_chg as change_percent,
                    volume,
                    amount,
                    volume_ratio
                FROM volume_stats
                WHERE """ + volume_condition + """
                ORDER BY ABS(pct_chg) DESC
                LIMIT 100
            """)
            
            result = self.db.execute(query, {"trade_date": formatted_date})
            stocks = result.fetchall()
            logger.debug("Found {} anomaly stocks", len(stocks))
            
            response_data = [
                {
                    "code": stock.code,
                    "name": stock.name,
                    "price": float(stock.price),
                    "changePercent": float(stock.change_percent),
                    "volume": float(stock.volume),
                    "amount": float(stock.amount),
                    "volumeRatio": float(stock.volume_ratio) if stock.volume_ratio else None
                }
                for stock in stocks
            ]
            
            logger.info("Successfully retrieved anomaly stocks for date: {}, type: {}", trade_date, type)
            return response_data
        except Exception as e:
            logger.error("Error in get_anomaly_stocks: {}", str(e))
            raise

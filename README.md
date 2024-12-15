# Stock Analysis Backend

基于 FastAPI 的股票市场分析后端系统。

## 功能特性

- 市场概览数据
- 板块资金流向
- 龙虎榜数据
- 概念题材分析
- 涨停板分析
- 技术分析指标

## 数据结构

### 数据库模型

1. IndexDailyBasic (指数每日基本面数据)
   - ts_code: 指数代码
   - trade_date: 交易日期
   - total_mv: 总市值
   - float_mv: 流通市值
   - pe_ttm: 市盈率TTM
   - pb: 市净率

2. StockDaily (个股每日交易数据)
   - ts_code: 股票代码
   - trade_date: 交易日期
   - close: 收盘价
   - pct_chg: 涨跌幅
   - amount: 成交额

### API数据模型

1. MarketOverviewData (市场概览数据)
   - tradeDate: 交易日期
   - shangzhengIndex: 上证指数
   - shangzhengChange: 上证涨跌幅
   - totalAmount: 总成交额
   - upCount: 上涨家数
   - downCount: 下跌家数

2. SectorFlowData (板块资金流向)
   - sectorName: 板块名称
   - inflow: 流入资金
   - outflow: 流出资金
   - netFlow: 净流入
   - stockList: 相关股票列表

3. TopListData (龙虎榜数据)
   - stockCode: 股票代码
   - stockName: 股票名称
   - price: 价格
   - change: 涨跌幅
   - amount: 成交额
   - buyList: 买入机构列表
   - sellList: 卖出机构列表

4. ConceptData (概念题材数据)
   - conceptName: 概念名称
   - stockCount: 概念股数量
   - avgChange: 平均涨跌幅
   - leadingStocks: 龙头股列表
   - description: 概念描述

5. LimitUpData (涨停板数据)
   - stockCode: 股票代码
   - stockName: 股票名称
   - limitUpTime: 涨停时间
   - limitUpReason: 涨停原因
   - turnoverRate: 换手率
   - amount: 成交额
   - bidAmount: 封单金额
   - bidTurnover: 封单比例
   - limitTimes: 连板数
   - status: 涨停状态（涨停、炸板）

6. TechnicalAnalysis (技术分析数据)
   - trend: 趋势分析
     - short_term: 短期趋势
     - medium_term: 中期趋势
     - long_term: 长期趋势
     - ma_cross: 均线交叉信号
   - macd: MACD分析
     - trend: MACD趋势
     - divergence: MACD差值
   - kdj: KDJ分析
     - k: K值
     - d: D值
     - j: J值
     - signal: 超买超卖信号
   - rsi: RSI分析
     - rsi6: 6日RSI
     - rsi12: 12日RSI
     - rsi24: 24日RSI
   - volatility: 波动率分析
     - value: 波动率值
     - trend: 波动趋势

## 技术栈

- FastAPI: Web框架
- SQLAlchemy: ORM框架
- PostgreSQL: 主数据库
- Redis: 缓存数据库
- Pandas: 数据处理

## 项目结构

```
app/
├── api/           # API路由和端点
├── core/          # 核心配置
├── market_view/   # 市场视图模块
├── models/        # 数据库模型
├── schemas/       # Pydantic数据模式
├── services/      # 业务逻辑服务
└── database.py    # 数据库配置
```

## 开发环境设置

1. 创建虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置环境变量：
复制 `.env.example` 到 `.env` 并填写相应配置：
- DATABASE_URL: PostgreSQL数据库连接URL
- REDIS_URL: Redis连接URL
- API_KEY: 数据源API密钥

4. 启动服务：

方法一：直接使用uvicorn启动（开发模式）
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

方法二：使用启动脚本（推荐）
```bash
# Linux/Mac
chmod +x start.sh
./start.sh

# Windows
start.bat
```

## API文档

启动服务后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 涨停板分析功能

涨停板分析模块提供了全面的涨停板数据分析功能，包括：

### 涨停板统计
- 首板、二板、三板及以上数量统计
- 行业和概念板块涨停分布
- 涨停原因分类统计
- 打板成功率分析

### 连板股追踪
- 连板天数统计
- 连板期间成交量变化
- 封单金额和封单比例
- 开板次数统计

### 个股详细分析
- 基本交易数据（开盘、最高、最低、收盘价等）
- 涨停时间和涨停原因
- 30日成交量分析（用于识别放量情况）
- 连板历史记录（包括每日成交量和换手率）

## API路由说明

所有API路由都以 `/api/v1` 为前缀，按功能模块组织：

### 市场分析接口

#### 市场概览
- GET `/market/overview/{trade_date}` - 获取市场概览数据
  - 返回：指数行情、市场资金、涨跌统计等

#### 板块资金流向
- GET `/market/sector-flow/{trade_date}` - 获取板块资金流向
  - 返回：行业板块和概念板块的资金流向数据

#### 龙虎榜
- GET `/market/top-list/{trade_date}` - 获取龙虎榜数据
  - 返回：个股龙虎榜、机构交易等信息

#### 涨停分析
- GET `/market/limit-analysis/{trade_date}` - 获取涨停板分析
  - 返回：涨停统计、行业分布、最强个股等
- GET `/market/limit-up` - 获取涨停板数据
  - 参数：
    - trade_date: 交易日期（YYYYMMDD）
    - limit_times: 连板数筛选
    - up_stat: 涨停统计筛选（如：3/4表示4天3板）

#### 股票详情
- GET `/stock/detail/{ts_code}` - 获取股票详细信息
  - 参数：
    - trade_date: 交易日期（YYYYMMDD）
  - 返回：基本信息、交易数据、涨停信息等

- GET `/stock/limit-history/{ts_code}` - 获取连板历史
  - 参数：
    - trade_date: 交易日期（YYYYMMDD）
  - 返回：连板期间的每日交易数据

- GET `/stock/volume-analysis/{ts_code}` - 获取成交量分析
  - 参数：
    - trade_date: 交易日期（YYYYMMDD）
  - 返回：30日成交量和价格走势数据

### 技术指标接口
- GET `/market/technical/{trade_date}` - 获取技术指标数据
  - 返回：市场技术指标分析数据

### 概念分析接口
- GET `/market/concepts/{trade_date}` - 获取概念题材数据
  - 返回：概念热度、资金流向等数据

所有接口都支持以下特性：
- 统一的错误处理和响应格式
- 请求参数验证
- 详细的日志记录
- CORS支持

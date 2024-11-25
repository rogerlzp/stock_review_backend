# Stock Analysis Backend

基于 FastAPI 的股票市场分析后端系统。

## 功能特性

- 市场概览数据
- 板块资金流向
- 龙虎榜数据
- 概念题材分析
- 涨停板分析

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

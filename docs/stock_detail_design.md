# 股票详情功能设计文档

## 功能概述

股票详情功能提供个股的详细信息展示，包括基本交易数据、涨停信息、连板历史和成交量分析等。

## 功能模块

### 1. 基本信息展示
- 股票代码和名称
- 当日交易数据
  - 开盘价、最高价、最低价、收盘价
  - 成交量、成交额
  - 换手率
- 涨停信息
  - 涨停时间
  - 涨停原因
  - 连板数
  - 封单金额和比例
  - 涨停状态（涨停中/开板/炸板）

### 2. 连板历史分析（针对连板股）
- 连板期间的每日交易数据
  - 日期
  - 成交量
  - 成交额
  - 换手率
- 连板天数统计
- 开板情况统计

### 3. 成交量分析
- 30日成交量走势图
  - 日期
  - 成交量柱状图
  - 价格折线图
- 放量标记
  - 相对于前期均量的倍数
  - 连续放量天数

## 数据库设计

### 表结构
1. limit_list_d（涨停板数据表）
```sql
CREATE TABLE limit_list_d (
    ts_code VARCHAR(10),       -- 股票代码
    trade_date VARCHAR(8),     -- 交易日期
    name VARCHAR(50),          -- 股票名称
    lu_time TIME,             -- 涨停时间
    lu_desc TEXT,             -- 涨停原因
    limit_times INT,          -- 连板数
    status VARCHAR(10),       -- 涨停状态
    theme VARCHAR(100),       -- 题材
    PRIMARY KEY (ts_code, trade_date)
);
```

2. kpl_list（交易数据表）
```sql
CREATE TABLE kpl_list (
    ts_code VARCHAR(10),       -- 股票代码
    trade_date VARCHAR(8),     -- 交易日期
    open DECIMAL(10,2),       -- 开盘价
    high DECIMAL(10,2),       -- 最高价
    low DECIMAL(10,2),        -- 最低价
    close DECIMAL(10,2),      -- 收盘价
    vol DECIMAL(20,2),        -- 成交量
    amount DECIMAL(20,2),     -- 成交额
    turnover_rate DECIMAL(10,2), -- 换手率
    bid_amount DECIMAL(20,2),  -- 封单金额
    bid_turnover DECIMAL(10,2), -- 封单比例
    PRIMARY KEY (ts_code, trade_date)
);
```

## API设计

### API 调用说明

前端调用 API 时有以下注意事项：

1. 前端不需要显式添加 `/api/v1` 前缀，这是由后端自动处理的
2. 前端代码中直接使用 `/api/market/stock/...` 这样的路径即可
3. 参数命名使用 camelCase 风格，如 `date` 而不是 `trade_date`

例如，获取股票详情的调用方式：
```typescript
// 前端代码
const response = await axios.get(`/api/market/stock/${stockCode}`, {
  params: {
    date: selectedDate
  }
})
```

### 1. 获取股票详情
```
GET /api/v1/market/stock/{ts_code}
参数：
- ts_code: 股票代码
- trade_date: 交易日期（YYYYMMDD）

返回：
{
    "stockCode": "605179.SH",
    "stockName": "名称",
    "limitUpTime": "09:30:00",
    "limitUpReason": "原因",
    "limitTimes": 2,
    "status": "涨停",
    "theme": "题材",
    "openPrice": 10.00,
    "highPrice": 11.00,
    "lowPrice": 10.00,
    "closePrice": 11.00,
    "volume": 1000000,
    "amount": 11000000,
    "turnoverRate": 5.2,
    "bidAmount": 5000000,
    "bidTurnover": 2.5
}
```

### 2. 获取连板历史
```
GET /api/v1/market/stock/{ts_code}/limit-history
参数：
- ts_code: 股票代码
- trade_date: 交易日期（YYYYMMDD）

返回：
[
    {
        "date": "20231210",
        "volume": 1000000,
        "amount": 11000000,
        "turnoverRate": 5.2
    },
    ...
]
```

### 3. 获取成交量分析
```
GET /api/v1/market/stock/{ts_code}/volume-analysis
参数：
- ts_code: 股票代码
- trade_date: 交易日期（YYYYMMDD）

返回：
{
    "dates": ["20231201", "20231202", ...],
    "volumes": [1000000, 1200000, ...],
    "prices": [10.00, 10.50, ...]
}
```

### 4. 获取股票对比数据
```
GET /api/v1/market/stock/compare/{ts_code}/{compare_code}
参数：
- ts_code: 第一只股票代码
- compare_code: 第二只股票代码
- start_date: 开始日期（YYYYMMDD）
- end_date: 结束日期（YYYYMMDD）

返回：
{
    "stock1": {
        "dates": ["20231201", "20231202", ...],
        "prices": {
            "close": [10.00, 10.50, ...],
            "high": [10.20, 10.70, ...],
            "low": [9.80, 10.30, ...],
            "open": [9.90, 10.40, ...]
        },
        "volumes": [1000000, 1200000, ...],
        "amounts": [10000000, 12000000, ...],
        "pct_chg": [2.5, -1.2, ...],
        "limit_info": {
            "dates": ["20231201", "20231202", ...],
            "turnover_ratio": [5.2, 4.8, ...],
            "fd_amount": [5000000, 4800000, ...],
            "limit_status": ["U", "Z", ...]
        }
    },
    "stock2": {
        // 与 stock1 结构相同
    },
    "correlation": {
        "price": 0.85,
        "volume": 0.72,
        "turnover": 0.68
    }
}
```

前端调用示例：
```typescript
// 前端代码
const response = await axios.get(`/api/market/stock/compare/${stock1Code}/${stock2Code}`, {
  params: {
    startDate: selectedStartDate,
    endDate: selectedEndDate
  }
});
```

## 实现注意事项

1. 数据处理
   - 使用 process_float 方法处理所有浮点数，避免 JSON 序列化错误
   - 对空值进行合理的默认值处理
   - 日期和时间格式的统一处理

2. 性能优化
   - 合理使用数据库索引
   - 避免重复查询
   - 考虑添加缓存机制

3. 错误处理
   - 统一的错误响应格式
   - 详细的日志记录
   - 友好的错误提示

4. 安全性
   - 参数验证
   - SQL注入防护
   - 访问控制

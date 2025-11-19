# Global Block Design

```text
+----------------------+        +-----------------+
|  CLI: backtest t1    | -----> | config / t1.json|
+----------------------+        +-----------------+
             |
             v
     +--------------------+
     | Backtest Engine    |  <--- 读取配置并初始化
     | (调度 fetcher / vm)|
     +--------------------+
             |
             v
     +--------------------+
     |      Fetcher       |  -- 优先查询缓存 -> 未命中则调用适配器
     | - check cache      |
     | - select adapter   |
     +--------------------+
         |        |
   缓存命中|        |调用适配器
         v        v
     +------+   +-----------------------------+
     |Cache |   | Adapter: yfinance/akshare/..|
     |(parquet)| | - fetch(symbol,start,end)  |
     +------+   +-----------------------------+
         \        /
          v      v
     +--------------------+
     | Local Storage      |  <-- 写入缓存 / 统一存储格式
     | (data_cache/...)   |
     +--------------------+
             |
             v
     +--------------------+
     | VirtualManager     |  <-- 装载策略，汇总各策略返回的 next_action
     | - load strategies  |
     | - aggregate actions|
     +--------------------+
             |
             v
     +--------------------+      （对每个交易日循环）
     |   Strategies (N)   | ---> 决策: decide(date, history) -> {sym: qty}
     +--------------------+
             |
             v
     +--------------------+
     | Execute / Update   |  <-- 以当日价格成交（buy/sell），更新持仓/现金/PNL
     | - apply next_action|
     | - update snapshots |
     +--------------------+
             |
             v
     +--------------------+
     | Daily Snapshots    |  <-- 存储逐日快照（资金曲线、持仓等）
     +--------------------+
             |
             v
     +--------------------+
     | Visualize / Report |  <-- 回测结束后生成图表与报告
     +--------------------+
```

---

## 运行流程概述

用户通过命令行发起回测任务（例如 `backtest t1`），回测引擎读取任务配置，初始化数据获取层（Fetcher）与虚拟基金管理器（VirtualManager）。Fetcher 优先从本地缓存读取历史数据；若未命中则调用对应适配器（如 yfinance、akshare）拉取并写入缓存。VirtualManager 装载一个或多个策略；每个交易日基于历史数据（不含当日）由各策略输出买/卖意图（按股数），管理器将所有策略的意图按股票求和得到当天的 net action，并以当日价格执行交易、更新持仓与资金。回测结束后，系统生成逐日快照与报告供可视化与分析使用。

---

## 模块清单与职责

- Backtest Engine：负责读取任务配置、协调 Fetcher 与 VirtualManager、启动按日循环并在结束后触发报告生成。  
- Fetcher（数据层）：统一缓存优先策略，按需加载适配器拉取数据并规范化写入本地统一存储。  
- VirtualManager（投资组合层）：装载任意数量策略，按日汇总策略动作并执行交易，记录逐笔交易与每日快照。  
- Adapter（适配器）：各数据源专用模块（yfinance、akshare、CSV 等），实现 fetch(symbol,start,end) 并返回统一格式数据。  
- Visualize：回测结束后生成图表与报告（资金曲线、持仓变化、绩效指标等）。

---
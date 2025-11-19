# VirtualManager 类 — 方法与接口摘要

概述：  
VirtualManager 是一个虚拟基金经理类，用于在回测环境中管理多策略组合、持仓、现金、交易历史与每日快照。按日调用已装载的策略生成当天操作（买/卖 X 股），将所有策略的返回值相加得到 net action 并在当日价格执行。

---

## 类：VirtualManager

### __init__(self, name: str, initial_cash: float = 100000.0)
- 功能：初始化管理器状态。
- 参数：name（账户名称）；initial_cash（初始现金，>=0）。
- 返回：None
- 要点：初始化 cash、positions、market prices、realized_pnl、history、daily_snapshots、strategies 等。

### add_strategy(self, strategy: Any) -> None
- 功能：向管理器添加策略实例。
- 参数：strategy（需实现 decide(date, history) 方法）。
- 返回：None
- 要点：校验策略包含可调用的 decide，否则抛错；不处理并发。

### update_market_price(self, symbol: str, price: float) -> None
- 功能：更新单个标的最新市价用于估值与未实现盈亏计算。
- 参数：symbol（代码）；price（非负价格）。
- 返回：None
- 要点：忽略 None 或负值输入。

### get_portfolio_value(self) -> float
- 功能：计算并返回账户当前总资产（现金 + 持仓市值）。
- 参数：无
- 返回：总资产（float）
- 要点：若某标的无 market price 则用 avg_cost 估算。

### get_unrealized_pnl(self) -> float
- 功能：计算并返回当前持仓的未实现盈亏。
- 参数：无
- 返回：未实现盈亏（float）
- 要点：按 (market_price - avg_cost) * quantity 累加。

### _buy_at(self, symbol: str, quantity: int, price: float, timestamp: Optional[datetime] = None) -> bool
- 功能：内部方法，以指定价格买入指定股数并更新现金与持仓。
- 参数：symbol、quantity（>0）、price（>0）、timestamp（可选）。
- 返回：交易是否成功（bool）
- 要点：若现金不足，按最大可买股数缩减；更新 avg_cost、market price、记录历史；不含手续费/滑点。

### _sell_at(self, symbol: str, quantity: int, price: float, timestamp: Optional[datetime] = None) -> bool
- 功能：内部方法，以指定价格卖出指定股数并更新现金、持仓与已实现盈亏。
- 参数：symbol、quantity（>0）、price（>0）、timestamp（可选）。
- 返回：交易是否成功（bool）
- 要点：若卖出量大于持仓则全部卖出；更新 realized_pnl、market price、记录历史。

### _aggregate_actions(self, date: pd.Timestamp, history: pd.DataFrame) -> Dict[str, int]
- 功能：调用所有已加载策略的 decide(date, history) 并对每个标的求和得到净买卖数量。
- 参数：date（当日），history（不含当日的过去价格 DataFrame）。
- 返回：symbol -> net_quantity（正为买/负为卖）。
- 要点：策略异常时忽略该策略本次输出；保证返回为整数字典。

### _execute_actions(self, actions: Dict[str, int], price_map: Dict[str, float], timestamp: Optional[datetime] = None) -> None
- 功能：根据汇总结果按给定价格执行买卖。
- 参数：actions（symbol->net_qty）、price_map（symbol->price）、timestamp（可选）。
- 返回：None
- 要点：若缺失价格或价格无效则跳过该标的；正数调用买入，负数调用卖出。

### run(self, price_df: pd.DataFrame) -> None
- 功能：按日迭代运行回测驱动流程：为每个交易日构造历史、调用策略、执行交易并记录快照。
- 参数：price_df（index 为日期的 DataFrame，columns 为 symbols，值为当日价格）。
- 返回：None
- 要点：对 index 强制转换为 DatetimeIndex 并排序；history = price_df.iloc[:i]（不含当日）；执行后记录 daily snapshot。

### _record_tx(self, action: str, symbol: str, quantity: int, price: float, timestamp: Optional[datetime] = None, meta: Optional[Dict[str, Any]] = None) -> None
- 功能：记录逐笔交易信息到 history。
- 参数：action（'BUY'/'SELL' 等）、symbol、quantity、price、timestamp、meta（可选）。
- 返回：None
- 要点：记录 cash_after、positions_snapshot、meta 等，便于回测回放与审计。

### _record_daily_snapshot(self, date: pd.Timestamp) -> None
- 功能：记录当日快照（现金、持仓、市场价、组合市值、盈亏等）。
- 参数：date（当日）。
- 返回：None
- 要点：将 snapshot 加入 daily_snapshots，用于生成逐日绩效曲线与分析。

### get_summary(self) -> Dict[str, Any]
- 功能：返回当前账户摘要，包含资金、持仓、估值与盈亏等。
- 参数：无
- 返回：包含 name、initial_cash、cash、positions、market_prices、portfolio_value、unrealized_pnl、realized_pnl、total_pnl、return_pct、n_positions、last_tx 的字典。

### get_history(self) -> List[Dict[str, Any]]
- 功能：返回逐笔交易历史的深拷贝。
- 参数：无
- 返回：history 列表副本。

### get_daily_snapshots(self) -> List[Dict[str, Any]]
- 功能：返回每日快照列表的深拷贝。
- 参数：无
- 返回：daily_snapshots 列表副本。

---

说明与扩展建议：  
- 当前模型为简化回测基础，不含手续费、滑点、部分成交、最小交易单位等复杂逻辑。  
- 可按需扩展：手续费/滑点模型、最小交易单位、限价/市价单类型、风险检查（RiskManager）和并发安全（策略并发执行隔离）。  
# Bitcoin Price Tracker

一个基于 Streamlit 的比特币价格显示应用，用于实时查看 BTC/USD 当前价格及 24 小时变化情况。

## 功能特性

- 实时显示比特币当前价格（USD）
- 显示 24 小时涨跌额
- 显示 24 小时涨跌幅
- 显示 24 小时最高价 / 最低价
- 支持手动刷新
- 支持缓存，减少重复请求
- 提供友好错误提示
- 请求失败时可回退展示最近一次成功数据

## 技术栈

- Python 3.10+
- Streamlit
- Requests
- CoinGecko API

## 项目结构

```bash
bitcoin-price-app/
├── app.py
├── requirements.txt
└── README.md
```

如需保留测试材料，可额外包含：

- `TEST_CASES.md`
- `TEST_REPORT_TEMPLATE.md`

## 快速开始

```bash
pip install -r requirements.txt
streamlit run app.py
```

启动后，浏览器会自动打开本地页面，默认地址一般为：

```bash
http://localhost:8501
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行方式

```bash
streamlit run app.py
```

## requirements.txt 示例

```txt
streamlit>=1.35.0
requests>=2.31.0
```

## 页面展示内容

应用页面主要展示以下内容：

- 当前价格（USD）
- 24小时涨跌额
- 24小时涨跌幅
- 24小时最高价
- 24小时最低价
- 市场趋势
- 数据源更新时间
- 最近数据获取时间
- 页面生成时间

## 刷新与缓存说明

- 页面使用 `st.cache_data(ttl=10)` 做 10 秒缓存
- 普通重新运行在 TTL 内会优先命中缓存
- 点击“刷新价格”按钮会主动清空缓存并重新请求最新数据

## 错误处理说明

应用处理了以下常见异常情况：

- 请求超时
- 网络连接失败
- HTTP 状态码异常
- JSON 数据异常
- 接口返回空数据或格式异常
- 关键字段缺失

当本次请求失败但之前已有成功数据时，页面会继续展示最近一次成功获取的数据，并提示当前为回退展示。

## 日志说明

- 应用日志默认输出到标准输出
- 运行时的详细错误信息可在控制台查看，便于排查问题

## 数据来源

- [CoinGecko API](https://www.coingecko.com/)
- 当前使用接口：
  - `/api/v3/coins/markets`

## 注意事项 / 已知限制

1. 当前应用依赖第三方公开 API，接口可用性和限流策略受外部服务影响
2. “最近数据获取时间”表示最近一次成功取数并缓存的时间
3. “页面生成时间”表示当前页面这次生成/更新的时间，不等同于数据源更新时间

## 后续可扩展方向

- 自动刷新
- 历史价格走势图
- 多币种支持（BTC / ETH / SOL）
- 多法币支持（USD / EUR / CNY）
- 深色主题
- 部署说明补充

## License

仅用于学习、演示与内部项目示例。
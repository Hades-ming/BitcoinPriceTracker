# Bitcoin Price Tracker - 部署说明

本文档说明如何在本地或服务器环境部署正式版应用。

---

## 1. 部署对象

正式版入口文件：

- `app.py`

测试增强版（仅测试用途）：

- `app_test.py`

> 正式环境请运行 `app.py`，不要运行 `app_test.py`。

---

## 2. 环境要求

- Python 3.10+
- 可访问公网，以请求 CoinGecko API
- 建议使用虚拟环境

---

## 3. 本地部署

### 3.1 创建虚拟环境（可选）

#### macOS / Linux
```bash
python -m venv .venv
source .venv/bin/activate
```

#### Windows PowerShell
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3.2 安装依赖

```bash
pip install -r requirements.txt
```

### 3.3 启动正式版

```bash
streamlit run app.py
```

默认访问地址通常为：

```text
http://localhost:8501
```

---

## 4. 服务器部署

### 4.1 基础命令

```bash
pip install -r requirements.txt
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

### 4.2 建议

- 使用 `screen`、`tmux`、`systemd` 或容器方式管理进程
- 通过 Nginx 反向代理暴露服务
- 仅开放必要端口
- 在公网部署时建议配置 HTTPS

---

## 5. Streamlit Cloud 部署

如果使用 Streamlit Cloud：

1. 将项目推送到 Git 仓库
2. 选择仓库并指定入口文件为 `app.py`
3. 安装依赖文件使用 `requirements.txt`
4. 部署后检查页面能否正常请求 CoinGecko API

---

## 6. 日志说明

- 应用日志默认输出到标准输出
- 请求异常、HTTP 错误、JSON 错误等会在控制台记录
- 页面仅向用户展示友好错误提示，不展示底层异常细节

---

## 7. 正式版 / 测试版说明

### 正式版
- 文件：`app.py`
- 用途：实际运行、演示、交付

### 测试增强版
- 文件：`app_test.py`
- 用途：代理测试、故障注入、异常回退验证

测试增强版默认不会显示测试工具；如需启用：

#### macOS / Linux
```bash
export ENABLE_TEST_MODE_UI=true
streamlit run app_test.py
```

#### Windows PowerShell
```powershell
$env:ENABLE_TEST_MODE_UI="true"
streamlit run app_test.py
```

> 不要在正式环境中启用测试 UI。

---

## 8. 已知限制

1. 应用依赖第三方公开 API，可能受到限流、波动或短暂不可用影响
2. 页面显示的“最近数据获取时间”是最近一次成功取数并缓存的时间
3. 页面显示的“页面生成时间”是当前页面生成/更新的时间
4. 目前仅支持 BTC / USD

---

## 9. 后续可选优化

- Docker 部署文件
- systemd 服务配置
- Nginx 反向代理示例
- 自动刷新
- 历史价格走势图
- 多币种支持
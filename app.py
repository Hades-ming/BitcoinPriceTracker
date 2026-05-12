from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Optional, TypedDict

import requests
import streamlit as st

# =========================
# 日志配置
# =========================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger(__name__)

# =========================
# 页面配置
# =========================
st.set_page_config(
    page_title="Bitcoin Price Tracker",
    page_icon="₿",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# =========================
# 常量配置
# =========================
PAGE_TITLE = "₿ Bitcoin Price Tracker"
PAGE_SUBTITLE = "实时查看比特币价格、24 小时涨跌额与涨跌幅（USD）"
COIN_LABEL = "当前币种：BTC / USD"

SPINNER_TEXT = "正在获取最新比特币价格..."
GENERIC_ERROR_TEXT = "暂时无法获取最新数据，请稍后重试。"
INITIAL_ERROR_TEXT = "暂时无法获取比特币价格，请稍后重试。"
FALLBACK_INFO_TEXT = "当前展示的是最近一次成功获取的数据。"

API_URL = "https://api.coingecko.com/api/v3/coins/markets"
API_PARAMS = {
    "vs_currency": "usd",
    "ids": "bitcoin",
}
REQUEST_TIMEOUT = 10
CACHE_TTL_SECONDS = 10
HEADERS = {
    "Accept": "application/json",
    "User-Agent": "bitcoin-price-tracker/1.0"
}


# =========================
# 类型定义
# =========================
class BitcoinPriceData(TypedDict):
    price: float
    change_24h: Optional[float]
    change_percent_24h: Optional[float]
    high_24h: Optional[float]
    low_24h: Optional[float]
    api_updated_at: Optional[str]
    data_fetched_at: str


# =========================
# 工具函数
# =========================
def to_optional_float(value: Any) -> Optional[float]:
    """安全转换为 Optional[float]。"""
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def format_currency(value: Any) -> str:
    """格式化货币。"""
    if value is None:
        return "N/A"
    try:
        return f"${float(value):,.2f}"
    except (TypeError, ValueError):
        return "N/A"


def format_percent(value: Any) -> str:
    """格式化百分比。"""
    if value is None:
        return "N/A"
    try:
        return f"{float(value):.2f}%"
    except (TypeError, ValueError):
        return "N/A"


def format_delta_currency(value: Any) -> str:
    """格式化涨跌额。"""
    if value is None:
        return "N/A"
    try:
        numeric = float(value)
        sign = "+" if numeric > 0 else ""
        return f"{sign}${numeric:,.2f}"
    except (TypeError, ValueError):
        return "N/A"


def format_delta_percent(value: Any) -> str:
    """格式化涨跌幅。"""
    if value is None:
        return "N/A"
    try:
        numeric = float(value)
        sign = "+" if numeric > 0 else ""
        return f"{sign}{numeric:.2f}%"
    except (TypeError, ValueError):
        return "N/A"


def get_trend_text(change_percent: Any) -> str:
    """生成趋势文案。"""
    try:
        value = float(change_percent)
        if value > 0:
            return "上涨中 📈"
        if value < 0:
            return "下跌中 📉"
        return "持平 ➖"
    except (TypeError, ValueError):
        return "趋势未知"


def parse_api_datetime(value: Optional[str]) -> str:
    """解析 API 时间字符串。"""
    if not value:
        return "N/A"

    try:
        normalized = value.replace("Z", "+00:00")
        dt = datetime.fromisoformat(normalized)
        return dt.isoformat(sep=" ", timespec="seconds")
    except ValueError:
        return value


def build_result_from_payload(btc: dict[str, Any]) -> BitcoinPriceData:
    """将 API payload 转换为统一结构。"""
    if btc.get("current_price") is None:
        logger.error("Missing required field current_price | payload=%s", btc)
        raise RuntimeError("缺少关键字段：current_price")

    recommended_fields = ["price_change_24h", "price_change_percentage_24h"]
    missing_recommended = [field for field in recommended_fields if btc.get(field) is None]
    if missing_recommended:
        logger.warning("Missing recommended fields: %s", missing_recommended)

    return {
        "price": float(btc["current_price"]),
        "change_24h": to_optional_float(btc.get("price_change_24h")),
        "change_percent_24h": to_optional_float(btc.get("price_change_percentage_24h")),
        "high_24h": to_optional_float(btc.get("high_24h")),
        "low_24h": to_optional_float(btc.get("low_24h")),
        "api_updated_at": btc.get("last_updated"),
        "data_fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


# =========================
# 数据获取函数
# =========================
@st.cache_data(ttl=CACHE_TTL_SECONDS)
def fetch_bitcoin_price() -> BitcoinPriceData:
    """获取 BTC/USD 市场数据，返回当前价格、24h 涨跌信息及更新时间。"""
    try:
        response = requests.get(
            API_URL,
            params=API_PARAMS,
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
    except requests.exceptions.Timeout as exc:
        logger.exception("Timeout while fetching bitcoin price")
        raise RuntimeError("请求超时，请稍后重试。") from exc
    except requests.exceptions.ConnectionError as exc:
        logger.exception("Connection error while fetching bitcoin price")
        raise RuntimeError("网络连接失败，请检查网络后重试。") from exc
    except requests.exceptions.HTTPError as exc:
        status_code = exc.response.status_code if exc.response is not None else "unknown"
        logger.exception("HTTP error while fetching bitcoin price, status=%s", status_code)
        raise RuntimeError(f"接口请求失败，状态码：{status_code}") from exc
    except requests.exceptions.RequestException as exc:
        logger.exception("Unexpected request error while fetching bitcoin price")
        raise RuntimeError("网络请求失败，请稍后重试。") from exc

    try:
        data = response.json()
    except ValueError as exc:
        logger.exception("Invalid JSON response from API")
        raise RuntimeError("接口返回数据格式异常。") from exc

    if not isinstance(data, list) or not data:
        logger.error("API returned empty or invalid list payload: %s", data)
        raise RuntimeError("接口返回数据为空或格式异常。")

    btc = data[0]
    if not isinstance(btc, dict):
        logger.error("BTC payload is not a dict: %s", btc)
        raise RuntimeError("比特币数据格式异常。")

    result = build_result_from_payload(btc)
    logger.info("Successfully fetched bitcoin price: %s", result["price"])
    return result


# =========================
# Session 状态初始化
# =========================
if "last_data" not in st.session_state:
    st.session_state.last_data = None

if "has_error" not in st.session_state:
    st.session_state.has_error = False


# =========================
# 页面样式
# =========================
st.markdown("""
<style>
    .main-title {
        text-align: center;
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        text-align: center;
        color: #666;
        margin-bottom: 1.2rem;
    }
    .price-card {
        padding: 1rem 1.2rem;
        border-radius: 16px;
        background: linear-gradient(135deg, #f8f9fa 0%, #eef2f7 100%);
        border: 1px solid #e6eaf0;
        margin-bottom: 1rem;
    }
    .footer-text {
        text-align: center;
        color: #888;
        font-size: 0.9rem;
        margin-top: 1rem;
    }
    .coin-tag {
        background: #f3f6fb;
        border: 1px solid #dbe4f0;
        color: #334155;
        padding: 0.75rem 1rem;
        border-radius: 12px;
        text-align: center;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# =========================
# 页面头部
# =========================
st.markdown(f'<div class="main-title">{PAGE_TITLE}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-title">{PAGE_SUBTITLE}</div>', unsafe_allow_html=True)

col_left, col_right = st.columns([1, 1])

with col_left:
    refresh_clicked = st.button("🔄 刷新价格", use_container_width=True)

with col_right:
    st.markdown(f'<div class="coin-tag">{COIN_LABEL}</div>', unsafe_allow_html=True)

if refresh_clicked:
    fetch_bitcoin_price.clear()
    logger.info("Manual refresh triggered by user")

# =========================
# 页面生成时间
# =========================
page_generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# =========================
# 数据加载
# =========================
btc_data: Optional[BitcoinPriceData] = None

with st.spinner(SPINNER_TEXT):
    try:
        btc_data = fetch_bitcoin_price()
        st.session_state.last_data = btc_data
        st.session_state.has_error = False
    except RuntimeError as exc:
        logger.warning("Failed to load bitcoin price data: %s", exc)
        btc_data = st.session_state.last_data
        st.session_state.has_error = True
    except Exception:
        logger.exception("Unexpected error while rendering page")
        btc_data = st.session_state.last_data
        st.session_state.has_error = True

# =========================
# 错误提示
# =========================
if st.session_state.has_error:
    if st.session_state.last_data:
        st.error(GENERIC_ERROR_TEXT)
        st.info(FALLBACK_INFO_TEXT)
    else:
        st.error(INITIAL_ERROR_TEXT)

# =========================
# 数据展示
# =========================
if btc_data:
    trend_text = get_trend_text(btc_data.get("change_percent_24h"))

    st.markdown('<div class="price-card">', unsafe_allow_html=True)
    st.metric(
        label="当前价格（USD）",
        value=format_currency(btc_data.get("price")),
        delta=format_delta_percent(btc_data.get("change_percent_24h"))
    )
    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            label="24小时涨跌额",
            value=format_delta_currency(btc_data.get("change_24h"))
        )
    with col2:
        st.metric(
            label="24小时涨跌幅",
            value=format_percent(btc_data.get("change_percent_24h"))
        )

    col3, col4 = st.columns(2)
    with col3:
        st.metric(
            label="24小时最高价",
            value=format_currency(btc_data.get("high_24h"))
        )
    with col4:
        st.metric(
            label="24小时最低价",
            value=format_currency(btc_data.get("low_24h"))
        )

    st.info(f"市场趋势：{trend_text}")
    st.caption(f"数据源更新时间：{parse_api_datetime(btc_data.get('api_updated_at'))}")
    st.caption(f"最近数据获取时间：{btc_data.get('data_fetched_at', 'N/A')}")
    st.caption(f"页面生成时间：{page_generated_at}")
else:
    if not st.session_state.has_error:
        st.warning("当前暂无可展示的比特币价格数据，请稍后重试或点击刷新。")

st.markdown(
    '<div class="footer-text">数据来源：CoinGecko API</div>',
    unsafe_allow_html=True
)
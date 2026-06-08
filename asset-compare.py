
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ======================
# 页面设置
# ======================
st.set_page_config(
    page_title="Asset Dashboard",
    layout="wide"
)

st.title("Asset Performance Dashboard")

# ======================
# 资产池
# ======================
asset_map = {
    "SPY": "SPY - S&P500(JPY计价)",
    "SPXL": "SPXL - 3x S&P500(JPY计价)",
    "^N225": "Nikkei 225(日经)",
    "1489.T": "日经高配当50",
    "1540.T": "Gold (JPY)",
    "BTC-JPY": "Bitcoin (BTC-JPY)",
    "000300.SS": "CSI300 - 沪深300(JPY计价)",
    "512890.SS": "中证红利低波(JPY计价)",
    "JPY=X": "USD/JPY",
    "CNYJPY=X": "CNY/JPY",
    "CHF=X": "USD/CHF",
    "CHFJPY=X": "CHF/JPY",
    "GBPEUR=X": "GBP/EUR",
    "AUDNZD=X": "AUD/NZD",
}

# ======================
# JPY计价转换
# ======================

# USD资产
usd_assets = [
    "SPY",
    "SPXL",
]

# CNY资产
cny_assets = [
    "000300.SS",
    "512890.SS",
]

# ======================
# FX杠杆
# ======================
fx_leverage = {
    "JPY=X": 18,
    "CHF=X": 18,
    "CHFJPY=X": 18,
    "GBPEUR=X": 18,
    "AUDNZD=X": 18,
}

# ======================
# 必选资产
# ======================
required_assets = [
    "JPY=X",
    "CNYJPY=X",
]

# ======================
# 可选资产
# ======================
options_list = [
    asset
    for asset in asset_map.keys()
    if asset not in required_assets
]

default_assets = options_list.copy()

# ======================
# 参数区
# ======================
st.caption("Base FX pairs (always enabled)")

required_labels = [
    asset_map.get(asset, asset)
    for asset in required_assets
]

st.write(", ".join(required_labels))

selected_assets = st.multiselect(
    "Select assets",
    options=options_list,
    default=default_assets
)

# 自动加入必选资产
selected_assets += required_assets

# 去重
selected_assets = list(dict.fromkeys(selected_assets))

period = st.selectbox(
    "Select period",
    ["1mo", "3mo", "1y", "3y", "5y"],
    index=1
)

# ======================
# 检查资产
# ======================
if len(selected_assets) == 0:
    st.warning("Please select at least one asset.")
    st.stop()

# ======================
# 数据下载函数
# ======================
@st.cache_data(ttl=3600)
def load_data(assets, period):

    raw = yf.download(
        assets,
        period=period,
        auto_adjust=True,
        progress=False,
        group_by="ticker"
    )

    data = {}

    # 多资产
    if len(assets) > 1:

        for ticker in assets:

            try:

                close_series = raw[ticker]["Close"]

                if not close_series.empty:
                    data[ticker] = close_series

            except Exception:
                pass

    # 单资产
    else:

        ticker = assets[0]

        data[ticker] = raw["Close"]

    df = pd.concat(data, axis=1)

    return df

# ======================
# 下载数据
# ======================
with st.spinner("Downloading market data..."):

    try:

        df = load_data(
            selected_assets,
            period
        )

    except Exception as e:

        st.error(f"Download failed: {e}")
        st.stop()

# ======================
# 数据整理
# ======================

# 时间排序
df = df.sort_index()

# 删除重复时间
df = df[~df.index.duplicated()]

# 前值填充
df = df.ffill()

# 删除全空列
df = df.dropna(axis=1, how="all")

if df.empty:
    st.error("No valid market data.")
    st.stop()

# ======================
# JPY计价转换
# ======================

# USD -> JPY
if "JPY=X" in df.columns:

    usd_jpy = df["JPY=X"]

    for asset in usd_assets:

        if asset in df.columns:

            df[asset] = (
                df[asset] * usd_jpy
            )

# CNY -> JPY
if "CNYJPY=X" in df.columns:

    cny_jpy = df["CNYJPY=X"]

    for asset in cny_assets:

        if asset in df.columns:

            df[asset] = (
                df[asset] * cny_jpy
            )

# ======================
# 收益率曲线
# ======================
returns = pd.DataFrame(index=df.index)

for col in df.columns:

    series = df[col].dropna()

    if len(series) < 2:
        continue

    leverage = fx_leverage.get(col, 1)

    # 日收益率
    daily_returns = (
        series.pct_change().fillna(0)
    )

    # 杠杆收益
    leveraged_daily = (
        daily_returns * leverage
    )

    # 累计收益率
    cumulative = (
        (1 + leveraged_daily).cumprod() - 1
    ) * 100

    returns[col] = cumulative

# ======================
# 绘图
# ======================
fig = go.Figure()

for col in returns.columns:

    fig.add_trace(
        go.Scatter(
            x=returns.index,
            y=returns[col],
            mode="lines",
            name=asset_map.get(col, col)
        )
    )

fig.update_layout(
    title="Asset Performance Comparison",
    template="plotly_dark",
    hovermode="x unified",
    height=700,

    xaxis_title="Date",
    yaxis_title="Return (%)",

    yaxis=dict(
        side="right"
    ),

    legend=dict(
        orientation="h",
        yanchor="top",
        y=-0.15,
        xanchor="center",
        x=0.5
    )
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ======================
# 指标计算
# ======================
metrics = pd.DataFrame()

for col in returns.columns:

    series = returns[col].dropna()

    if len(series) < 2:
        continue

    # 总收益
    total_return = series.iloc[-1]

    # 恢复净值曲线
    equity = (
        1 + series / 100
    )

    # 日收益率
    daily_returns = (
        equity.pct_change().dropna()
    )

    # 波动率
    vol = (
        daily_returns.std() * np.sqrt(252)
    ) * 100

    # Sharpe
    sharpe = (
        daily_returns.mean() / daily_returns.std()
    ) * np.sqrt(252)

    # 最大回撤
    rolling_max = equity.cummax()

    drawdown = (
        equity / rolling_max - 1
    )

    max_dd = (
        drawdown.min()
    ) * 100

    # Calmar
    calmar = (
        total_return / abs(max_dd)
    ) if max_dd != 0 else np.nan

    metrics.loc[col, "Total Return %"] = total_return
    metrics.loc[col, "Volatility %"] = vol
    metrics.loc[col, "Sharpe"] = sharpe
    metrics.loc[col, "Max Drawdown %"] = max_dd
    metrics.loc[col, "Calmar"] = calmar

# 保留两位小数
metrics = metrics.round(2)

# 按总收益排序
metrics = metrics.sort_values(
    by="Total Return %",
    ascending=False
)

# 替换显示名称
metrics.index = [
    asset_map.get(i, i)
    for i in metrics.index
]

# ======================
# 展示指标
# ======================
st.subheader("Performance Metrics")

st.dataframe(
    metrics,
    use_container_width=True
)


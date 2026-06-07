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
    "^N225": "Nikkei 225 (日经)",
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

# 美元资产
usd_assets = [
    "SPY",
    "SPXL",
]

# 人民币资产
cny_assets = [
    "000300.SS",
    "512890.SS",
]

# ======================
# 必选资产
# ======================
required_assets = [
    "JPY=X",
    "CNYJPY=X"
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
    #["1y", "3y", "5y", "10y", "max"],
    ["1mo","3mo","1y", "3y", "5y"],
    index=1
)


# ======================
# 检查资产
# ======================
if len(selected_assets) == 0:
    st.warning("Please select at least one asset.")
    st.stop()

# ======================
# 下载数据（批量）
# ======================
with st.spinner("Downloading market data..."):

    try:

        raw = yf.download(
            selected_assets,
            period=period,
            auto_adjust=True,
            progress=False,
            group_by="ticker"
        )

        data = {}

        # 多资产
        if len(selected_assets) > 1:

            for ticker in selected_assets:

                try:

                    close_series = raw[ticker]["Close"]

                    if not close_series.empty:
                        data[ticker] = close_series

                except Exception:
                    st.warning(f"No data: {ticker}")

        # 单资产
        else:

            ticker = selected_assets[0]

            data[ticker] = raw["Close"]

        # 合并
        df = pd.concat(data, axis=1)

    except Exception as e:

        st.error(f"Download failed: {e}")
        st.stop()

# ======================
# 缺失值处理
# ======================
df = df.ffill()

# 删除全空列
df = df.dropna(axis=1, how="all")

# 如果仍为空
if df.empty:
    st.error("No valid market data.")
    st.stop()

# ======================
# 资产转换为JPY计价
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
# 杠杆设置
# ======================
leveraged_assets = {
    "JPY=X": 18,
    "CNYJPY=X": 18,
    "CHF=X": 18,
    "CHFJPY=X": 18,
    "GBPEUR=X": 18,
    "AUDNZD=X": 18,
}

# ======================
# Normalize 收益率
# ======================
returns = df.copy()

for col in returns.columns:

    valid = returns[col].dropna()

    # 空数据跳过
    if len(valid) == 0:
        continue

    first_valid = valid.iloc[0]

    # 默认无杠杆
    leverage = leveraged_assets.get(col, 1)

    # 收益率归一化 + 杠杆
    returns[col] = (
        (
            returns[col] / first_valid
            - 1
        )
        * 100
        * leverage
    )

# ======================
# Plotly 绘图
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

for col in df.columns:

    series = df[col].dropna()

    # 数据太少跳过
    if len(series) < 2:
        continue

    # 日收益率
    daily_returns = series.pct_change().dropna()

    # 实际年数
    years = (
        (series.index[-1] - series.index[0]).days
    ) / 365.25

    # CAGR
    cagr = (
        (series.iloc[-1] / series.iloc[0]) ** (1 / years) - 1
    ) * 100

    # Volatility
    vol = (
        daily_returns.std() * np.sqrt(252)
    ) * 100

    # Sharpe
    sharpe = (
        (cagr / 100) / (vol / 100)
    ) if vol != 0 else np.nan

    # Max Drawdown
    rolling_max = series.cummax()

    drawdown = (
        series / rolling_max - 1
    )

    max_dd = (
        drawdown.min()
    ) * 100

    # Calmar
    calmar = (
        abs(cagr / max_dd)
    ) if max_dd != 0 else np.nan

    metrics.loc[col, "CAGR %"] = cagr
    metrics.loc[col, "Volatility %"] = vol
    metrics.loc[col, "Sharpe"] = sharpe
    metrics.loc[col, "Max Drawdown %"] = max_dd
    metrics.loc[col, "Calmar"] = calmar

# 保留两位小数
metrics = metrics.round(2)

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
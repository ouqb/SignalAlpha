import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.title("Asset Performance Dashboard")

# ======================
# 1. 资产池（统一管理）
# ======================
asset_map = {
    "SPY": "SPY (S&P500 ETF)",
    "SPXL": "SPXL (3x S&P500)",
    "^N225": "Nikkei 225 (日经)",
    "000300.SS": "CSI300 (沪深300)",
    "GLD": "Gold ETF (黄金)",
    "BTC-USD": "Bitcoin (BTC)"
}

# ======================
# 2. 多选框
# ======================
selected_assets = st.multiselect(
    "Select assets to compare",
    options=list(asset_map.keys()),
    default=list(asset_map.keys())
)

if len(selected_assets) == 0:
    st.warning("Please select at least one asset.")
    st.stop()

# ======================
# 3. 下载数据
# ======================
data = {}

for ticker in selected_assets:
    df = yf.download(ticker, start="2020-01-01", auto_adjust=True)
    if not df.empty:
        data[ticker] = df["Close"].squeeze()

# ======================
# 4. 合并数据
# ======================
df = pd.concat(data, axis=1)
df = df.dropna()

# ======================
# 5. 计算收益率
# ======================
returns = (df / df.iloc[0] - 1) * 100

# ======================
# 6. 画图
# ======================
fig = go.Figure()

for col in returns.columns:
    fig.add_trace(go.Scatter(
        x=returns.index,
        y=returns[col],
        mode="lines",
        name=asset_map.get(col, col)
    ))

fig.update_layout(
    title="Asset Performance Comparison",
    xaxis_title="Date",
    yaxis_title="Return (%)",
    hovermode="x unified",
    template="plotly_dark",
    legend=dict(
        orientation="h",
        yanchor="top",
        y=-0.2,
        xanchor="center",
        x=0.5
    )
)

st.plotly_chart(fig, use_container_width=True)
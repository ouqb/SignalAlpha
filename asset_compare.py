import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 下载数据
nikkei = yf.download("^N225", start="2020-01-01", auto_adjust=True)
hs300 = yf.download("000300.SS", start="2020-01-01", auto_adjust=True)
spy = yf.download("SPY", start="2020-01-01", auto_adjust=True)

# 提取 Close 并转成 Series
nikkei_close = nikkei["Close"].squeeze()
hs300_close = hs300["Close"].squeeze()
spy_close = spy["Close"].squeeze()

# 合并
df = pd.concat([
    nikkei_close.rename("Nikkei225"),
    hs300_close.rename("HS300"),
    spy_close.rename("SPY")
], axis=1)

# 删除空值
df = df.dropna()

# 计算涨跌幅(%)
returns = (df / df.iloc[0] - 1) * 100

name_map = {
    "Nikkei225": "日经 (Nikkei225)",
    "HS300": "沪深300 (HS300)",
    "SPY": "标普500ETF (SPY)"
}

# Plotly 图表
fig = go.Figure()

for col in returns.columns:
    fig.add_trace(go.Scatter(
        x=returns.index,
        y=returns[col],
        mode="lines",
        name=name_map[col]
    ))

fig.update_layout(
    title="Asset Performance Comparison",
    xaxis_title="Date",
    yaxis_title="Return (%)",
    hovermode="x unified",
    template="plotly_dark"
)

st.plotly_chart(fig, use_container_width=True)
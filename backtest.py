import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 页面标题
st.title("SignalAlpha Dashboard")

# ===== 资产选择 =====
symbol = st.selectbox(
    "Symbol",
    ["SPY", "SPXL","^N225", "000300.SS", "GLD", "BTC-USD"]
)

# ===== 参数区（折叠）=====
with st.expander("Parameters", expanded=True):
    short_ma = st.number_input("Short MA", min_value=1, max_value=500, value=25)
    long_ma = st.number_input("Long MA", min_value=1, max_value=500, value=100)

# ===== 下载数据 =====
data = yf.download(
    symbol,
    period="5y",
    auto_adjust=True
)

# 如果是多层列则降级
if isinstance(data.columns, pd.MultiIndex):
    data.columns = data.columns.droplevel(1)

# ===== 计算均线 =====
data["ShortMA"] = data["Close"].rolling(short_ma).mean()
data["LongMA"] = data["Close"].rolling(long_ma).mean()

# ===== 创建图表 =====
fig = go.Figure()

# Close价格
fig.add_trace(
    go.Scatter(
        x=data.index,
        y=data["Close"],
        mode="lines",
        name=symbol
    )
)

# 短MA
fig.add_trace(
    go.Scatter(
        x=data.index,
        y=data["ShortMA"],
        mode="lines",
        name=f"MA{short_ma}"
    )
)

# 长MA
fig.add_trace(
    go.Scatter(
        x=data.index,
        y=data["LongMA"],
        mode="lines",
        name=f"MA{long_ma}"
    )
)

# 图表布局
fig.update_layout(
    title=f"{symbol} MA Analysis",
    xaxis_title="Date",
    yaxis_title="Price",
    template="plotly_dark"
)

# 显示图表
st.plotly_chart(fig, use_container_width=True)
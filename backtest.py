import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 标题
st.title("S&P500 Chart")

# 下载数据
data = yf.download(
    "SPY",
    period="5y",
    auto_adjust=True
)
# 如果是多层列则降级
if isinstance(data.columns, pd.MultiIndex):
    data.columns = data.columns.droplevel(1)

# 计算均线
data["MA25"] = data["Close"].rolling(25).mean()
data["MA100"] = data["Close"].rolling(100).mean()


# 创建图表
fig = go.Figure()

# Close价格
fig.add_trace(
    go.Scatter(
        x=data.index,
        y=data["Close"],
        mode="lines",
        name="S&P500"
    )
)

# MA25
fig.add_trace(
    go.Scatter(
        x=data.index,
        y=data["MA25"],
        mode="lines",
        name="MA25"
    )
)

# MA100
fig.add_trace(
    go.Scatter(
        x=data.index,
        y=data["MA100"],
        mode="lines",
        name="MA100"
    )
)

# 图表布局
fig.update_layout(
    title="SPY Chart with Moving Averages",
    xaxis_title="Date",
    yaxis_title="Price",
    template="plotly_dark"
)

# 显示图表
st.plotly_chart(
    fig,
    use_container_width=True
)







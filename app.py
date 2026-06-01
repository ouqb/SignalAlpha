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
# 去掉第二层列 
data.columns = data.columns.droplevel(1)

# 后台打印
print("========== DATA ==========")
print(data)

print("========== COLUMNS ==========")
print(data.columns)

print("========== HEAD ==========")
print(data.head())

print("========== TAIL ==========")
print(data.tail())

print("========== INFO ==========")
print(data.info())

# 创建图表
fig = go.Figure()

# 折线图
fig.add_trace(
    go.Scatter(
        x=data.index,          # 横轴 Date
        y=data["Close"],       # 纵轴 Close
        mode="lines",
        name="Close"
    )
)

# 设置标题
fig.update_layout(
    title="SPY Chart",
    xaxis_title="Date",
    yaxis_title="Close"
)

# 显示图表
st.plotly_chart(
    fig,
    use_container_width=True
)







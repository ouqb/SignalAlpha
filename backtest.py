import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 页面标题
st.title("SignalAlpha Dashboard")

# ===== 用户输入 =====

short_ma = st.number_input(
    "Short MA",
    min_value=1,
    max_value=500,
    value=25
)

long_ma = st.number_input(
    "Long MA",
    min_value=1,
    max_value=500,
    value=100
)

update_button = st.button("Update Chart")

# ===== 下载数据 =====

data = yf.download(
    "SPY",
    period="5y",
    auto_adjust=True
)

# 多层列处理
if isinstance(data.columns, pd.MultiIndex):
    data.columns = data.columns.droplevel(1)

# ===== 只有按按钮才更新 =====

#if update_button:

    # 计算均线
    data["ShortMA"] = data["Close"].rolling(short_ma).mean()
    data["LongMA"] = data["Close"].rolling(long_ma).mean()

    # 创建图表
    fig = go.Figure()

    # 收盘价
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data["Close"],
            mode="lines",
            name="SPY"
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
        title="SignalAlpha MA Analysis",
        xaxis_title="Date",
        yaxis_title="Price",
        template="plotly_dark"
    )

    # 显示图表
    st.plotly_chart(
        fig,
        use_container_width=True
    )
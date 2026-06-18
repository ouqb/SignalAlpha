import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import numpy as np

symbols = {
    "沪深300": "000300.SS",
    "红利低波ETF": "512890.SS",
    "黄金ETF": "518880.SS",
}

period = st.selectbox(
    "Select period",
    ["1mo", "3mo", "6mo", "1y", "3y", "5y"],
    index=1
)

df = yf.download(
    list(symbols.values()),
    period=period,
    auto_adjust=True,
    progress=False
)["Close"]

df = df.dropna()

# 改成中文列名
df.columns = symbols.keys()

# 转换为累计收益率(%)
returns = (df / df.iloc[0] - 1) * 100

# Plotly
fig = go.Figure()

for col in returns.columns:
    # 原曲线
    fig.add_trace(
        go.Scatter(
            x=returns.index,
            y=returns[col],
            mode="lines",
            name=col,
        )
    )

    # ===== 计算趋势线 =====
    x = np.arange(len(returns))
    y = returns[col].values

    slope, intercept = np.polyfit(x, y, 1)

    trend = slope * x + intercept

    fig.add_trace(
        go.Scatter(
            x=returns.index,
            y=trend,
            mode="lines",
            name=f"{col} 趋势",
            line=dict(dash="dash"),
            showlegend=True,
        )
    )

fig.update_layout(
    title="累计收益率比较",
    xaxis_title="日期",
    yaxis_title="收益率 (%)",
    hovermode="x unified",
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    )
)

st.plotly_chart(fig, use_container_width=True)
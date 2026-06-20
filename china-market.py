import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import numpy as np

symbols = {
    "沪深300": "000300.SS",
    "红利低波ETF": "512890.SS",
    "黄金ETF": "518880.SS",
    "标普500": "^GSPC",
    "美元兑人民币": "CNY=X",
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

# 改成中文列名
df = df.rename(columns={symbol: name for name, symbol in symbols.items()})

# 用美元标普500乘以美元兑人民币汇率，得到人民币计价的标普500
df["人民币计价标普500"] = df["标普500"] * df["美元兑人民币"]
df = df.drop(columns=["标普500", "美元兑人民币"])
df = df.dropna()

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
    margin=dict(b=110),
    legend=dict(
        orientation="h",
        yanchor="top",
        y=-0.4,
        xanchor="left",
        x=0,
        entrywidth=0.5,
        entrywidthmode="fraction",
    )
)

st.plotly_chart(fig, use_container_width=True)

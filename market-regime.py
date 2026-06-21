import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# =========================
# 组合配置
# =========================

PORTFOLIOS = {
    "china": {
        "title": "中国资产比较",
        "symbols": {
            "沪深300": "000300.SS",
            "红利低波ETF": "512890.SS",
            "黄金ETF": "518880.SS",
            "标普500": "^GSPC",
            "美元兑人民币": "CNY=X",
        },
        "final_order": [
            "沪深300",
            "红利低波ETF",
            "黄金ETF",
            "人民币计价标普500",
        ],
    },
    "japan": {
        "title": "日本资产比较",
        "symbols": {
            "日经225": "^N225",
            "日经高配当ETF": "1489.T",
            "黄金ETF": "1328.T",
            "标普500": "^GSPC",
            "美元兑日元": "JPY=X",
        },
        "final_order": [
            "日经225",
            "日经高配当ETF",
            "黄金ETF",
            "日元计价标普500",
        ],
    },
}

# =========================
# URL参数
# ?p=china
# ?p=japan
# =========================

portfolio = st.query_params.get("p", "china")

if portfolio not in PORTFOLIOS:
    portfolio = "china"

config = PORTFOLIOS[portfolio]

st.title(config["title"])

# =========================
# 时间范围
# =========================

period = st.selectbox(
    "选择时间范围",
    ["1mo", "3mo", "6mo", "1y", "3y", "5y"],
    index=1,
)

# =========================
# 下载数据
# =========================

symbols = config["symbols"]

df = yf.download(
    list(symbols.values()),
    period=period,
    auto_adjust=True,
    progress=False,
)["Close"]

# ticker -> 中文名
df = df.rename(
    columns={symbol: name for name, symbol in symbols.items()}
)

# =========================
# 本币计价 S&P500
# =========================

if portfolio == "china":

    df["人民币计价标普500"] = (
        df["标普500"] * df["美元兑人民币"]
    )

    df = df.drop(
        columns=["标普500", "美元兑人民币"]
    )

elif portfolio == "japan":

    # JPY=X = USDJPY
    df["日元计价标普500"] = (
        df["标普500"] * df["美元兑日元"]
    )

    df = df.drop(
        columns=["标普500", "美元兑日元"]
    )

# =========================
# 强制列顺序
# =========================

df = df[config["final_order"]]

# =========================
# 累计收益率
# 每个资产按自己的起点归一化
# =========================

returns = pd.DataFrame(index=df.index)

for col in df.columns:

    series = df[col]

    valid = series.dropna()

    if len(valid) == 0:
        continue

    first_value = valid.iloc[0]

    returns[col] = (
        series / first_value - 1
    ) * 100

# =========================
# 绘图
# =========================

fig = go.Figure()

for col in returns.columns:

    valid = returns[col].dropna()

    if len(valid) < 2:
        continue

    # 主曲线
    fig.add_trace(
        go.Scatter(
            x=valid.index,
            y=valid.values,
            mode="lines",
            name=col,
        )
    )

    # 趋势线
    x = np.arange(len(valid))
    y = valid.values

    slope, intercept = np.polyfit(x, y, 1)

    trend = slope * x + intercept

    fig.add_trace(
        go.Scatter(
            x=valid.index,
            y=trend,
            mode="lines",
            name=f"{col} 趋势",
            line=dict(
                dash="dash",
            ),
        )
    )

# =========================
# 布局
# =========================

fig.update_layout(
    title=f"{config['title']}（累计收益率）",
    xaxis_title="日期",
    yaxis_title="收益率 (%)",
    hovermode="x unified",
    margin=dict(
        l=20,
        r=20,
        t=60,
        b=140,
    ),
    legend=dict(
        orientation="h",
        yanchor="top",
        y=-0.35,
        xanchor="left",
        x=0,
        entrywidth=0.5,
        entrywidthmode="fraction",
    ),
)

st.plotly_chart(
    fig,
    use_container_width=True,
    config={
        "staticPlot": True,
        "displayModeBar": False,
    },
)
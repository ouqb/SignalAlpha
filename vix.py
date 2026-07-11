import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide")

st.title("CBOE VIX Dashboard")

urls = {
    "VIX9D": "https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX9D_History.csv",
    "VIX": "https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv",
    "VIX3M": "https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX3M_History.csv",
}

dfs = {}

for name, url in urls.items():

    try:
        df = pd.read_csv(url)

        df["DATE"] = pd.to_datetime(df["DATE"])
        df = df.set_index("DATE")

        dfs[name] = df["CLOSE"]

    except Exception as e:
        st.error(f"{name} Failed")
        st.write(e)

if len(dfs) == 0:
    st.stop()

data = pd.DataFrame(dfs)

# 只显示最近10个交易日
data = data.tail(10)

fig = go.Figure()

for col in data.columns:
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data[col],
            mode="lines+markers",
            name=col,
        )
    )

fig.update_layout(
    title="CBOE Volatility Index (Last 10 Trading Days)",
    height=450,
    hovermode="x unified",
    xaxis_title="Date",
    yaxis_title="Value",
    legend=dict(
        orientation="h",
        y=1.08,
        x=0,
    ),
)

fig.update_layout(
    dragmode=False,
    xaxis=dict(fixedrange=True),
    yaxis=dict(fixedrange=True),
)



st.plotly_chart(
    fig,
    use_container_width=True,
    config={
        "displayModeBar": False,
        "scrollZoom": False,
        "doubleClick": False,
    },
)

st.subheader("Latest 10 Trading Days")

st.dataframe(
    data.iloc[::-1],   # 最新日期显示在最上面
    use_container_width=True,
)
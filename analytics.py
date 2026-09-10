import pandas as pd


import plotly.express as px


import plotly.graph_objects as go


import streamlit as st


from design import FACTION_COLORS


@st.cache_data(show_spinner=False)
def load_data(csv_bytes: bytes) -> pd.DataFrame:
    df = pd.read_csv(pd.io.common.BytesIO(csv_bytes), dtype={"source": "string", "reason": "string"})
    required = ["logTimestamp", "faction", "planet", "regionName", "reason", "pointValue", "multiplier", "source"]
    if not set(required).issubset(df.columns):
        raise ValueError("CSV is missing required scoring columns")
    df = df[[c for c in required + ["planetModifier", "softCapMultiplier"] if c in df.columns]].copy()
    raw_time = df["logTimestamp"]
    df["logTimestamp"] = pd.to_datetime(raw_time, format="%b %d, %Y @ %H:%M:%S.%f", errors="coerce", utc=True)
    missing = df["logTimestamp"].isna()
    df.loc[missing, "logTimestamp"] = pd.to_datetime(raw_time[missing], format="ISO8601", errors="coerce", utc=True)
    if df["logTimestamp"].isna().any() or df.empty:
        raise ValueError("CSV has invalid timestamps or no scoring rows")
    df["source"] = df["source"].where(df["source"].str.fullmatch(r"-?[0-9]+", na=False), "unknown")
    df["pointValue"] = pd.to_numeric(df["pointValue"], errors="coerce").fillna(0)
    df["planet"] = df["planet"].fillna("unknown").replace({"null": "unknown"})
    df["faction"] = df["faction"].fillna("unknown")
    df["reason"] = df["reason"].fillna("unknown")
    df["type"] = df["reason"]
    df["source"] = df["source"].fillna("unknown").astype("string")
    return df


def grouped_totals(df: pd.DataFrame, primary: str, split_by: str) -> pd.DataFrame:
    if split_by == "None":
        result = (
            df.groupby(primary, dropna=False, as_index=False)["pointValue"]
            .sum()
            .sort_values("pointValue", ascending=False)
        )
        result["split"] = "All"
        return result.rename(columns={primary: "group"})

    result = (
        df.groupby([primary, split_by], dropna=False, as_index=False)["pointValue"]
        .sum()
        .sort_values("pointValue", ascending=False)
    )
    return result.rename(columns={primary: "group", split_by: "split"})


def chart_frame(df: pd.DataFrame, index_col: str, column_col: str, value_col: str) -> pd.DataFrame:
    frame = df.pivot_table(
        index=index_col,
        columns=column_col,
        values=value_col,
        aggfunc="sum",
        fill_value=0,
    )
    return frame.sort_index()


def grouped_timeseries(df: pd.DataFrame, time_grain: str, group_col: str, value_mode: str) -> pd.DataFrame:
    freq = "D" if time_grain == "Daily" else "h"
    prepared = df.assign(period=df["logTimestamp"].dt.floor(freq))
    if value_mode == "Points":
        grouped = (
            prepared.groupby(["period", group_col], as_index=False)["pointValue"]
            .sum()
            .rename(columns={"pointValue": "value"})
        )
    else:
        grouped = (
            prepared.groupby(["period", group_col], as_index=False)
            .size()
            .rename(columns={"size": "value"})
        )
    return chart_frame(grouped, "period", group_col, "value")


def ordered_faction_columns(frame: pd.DataFrame) -> pd.DataFrame:
    ordered = [name for name in ["Rebel", "Imperial"] if name in frame.columns]
    ordered.extend([name for name in frame.columns if name not in ordered])
    return frame[ordered]


def faction_line_figure(frame: pd.DataFrame, title_y: str) -> go.Figure:
    frame = ordered_faction_columns(frame)
    fig = go.Figure()
    for column in frame.columns:
        fig.add_trace(
            go.Scatter(
                x=frame.index,
                y=frame[column],
                mode="lines",
                name=column,
                line={"color": FACTION_COLORS.get(column, "#9aa5b1"), "width": 3},
            )
        )
    fig.update_layout(
        height=320,
        margin={"l": 10, "r": 10, "t": 10, "b": 10},
        yaxis_title=title_y,
        legend_title_text="Faction",
    )
    return fig


def breakdown_bar_figure(df: pd.DataFrame, primary_dimension: str) -> go.Figure:
    fig = px.bar(
        df,
        x="pointValue",
        y="group",
        color="split",
        orientation="h",
        labels={"pointValue": "Points", "group": primary_dimension.title(), "split": "Split"},
    )
    if set(df["split"].unique()).issubset(set(FACTION_COLORS) | {"All"}):
        color_map = {**FACTION_COLORS, "All": "#90a4ae"}
        for trace in fig.data:
            trace.marker.color = color_map.get(trace.name, "#90a4ae")
    fig.update_layout(height=350, margin={"l": 10, "r": 10, "t": 10, "b": 10}, yaxis={"categoryorder": "total ascending"})
    return fig


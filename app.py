from pathlib import Path
import os
import pandas as pd
import plotly.express as px
import streamlit as st
from analytics import load_data, grouped_totals, grouped_timeseries, faction_line_figure, breakdown_bar_figure
from cycles import available_cycles
from design import setup, header, chart, table, date, FACTION_COLORS
from event_view import show_latest_event

setup()
ROOT = Path(__file__).parent
ARCHIVE = Path(os.environ.get("GCW_DATA_DIR", str(ROOT / "data" / "published")))

st.sidebar.markdown("### GCW Observatory")
view = st.sidebar.radio("Explore", ["GCW cycles", "Latest Shatterpoint"])
if view == "Latest Shatterpoint":
    show_latest_event(ARCHIVE / "latest_event.json")
    st.stop()

cycles = [c for c in available_cycles(ARCHIVE) if c.get("regional_rows", 0) > 0]
choices = {c["start"]: (f"{date(c['start'])} – {date(c['end_exclusive'])}", ARCHIVE / c["directory"] / "gcw_points.csv", c) for c in cycles}
choices["historical"] = ("Feb 22 – Mar 27, 2026", ROOT / "data" / "gcw_points.csv", None)
selected = st.sidebar.selectbox("GCW cycle", list(choices), format_func=lambda key: choices[key][0])
label, path, metadata = choices[selected]
try:
    df = load_data(path.read_bytes())
except (OSError, ValueError):
    header("GCW Observatory")
    st.error("This cycle is temporarily unavailable. Please select another cycle.")
    st.stop()
df["planet"] = df.planet.str.replace("_", " ").str.title()
type_names = {
    "Factional base control": "Base control", "factional presence": "Factional presence",
    "delivering supplies (PvE)": "Supply deliveries (PvE)", "a PvP kill": "PvP kills",
    "participating in a PvP Space Battle": "PvP space participation", "winning a PvP Space Battle": "PvP space victories",
    "participating in a PvE Space Battle": "PvE space participation", "winning a PvE Space Battle": "PvE space victories",
    "participating in a Flashpoint": "Flashpoint participation", "winning a Flashpoint": "Flashpoint victories",
    "intercepting supplies": "Supply interceptions", "generating supplies": "Supply production",
    "building up an Invasion": "Invasion preparation", "participating in an Invasion": "Invasion participation",
    "winning an Invasion": "Invasion victories", "a Restuss PvE mission completion": "Restuss PvE missions",
    "a PvE Duty mission wave": "PvE duty waves", "a PvE Duty mission completion": "PvE duty missions",
    "a PvP Duty mission wave": "PvP duty waves", "a PvP Duty mission completion": "PvP duty missions",
    "the destruction of a Faction Base": "Base destruction", "the destruction of a PvP Faction Base": "PvP base destruction",
    "the defense of a Faction Base": "Base defense", "the defense of a PvP Faction Base": "PvP base defense",
    "an Imperial Crackdown": "Imperial Crackdowns", "a Rebel Uprising": "Rebel Uprisings",
}
df["type"] = df.type.replace(type_names)
minimum, maximum = df.logTimestamp.min(), df.logTimestamp.max()

header("GCW Observatory")
st.subheader(label)
st.caption(f"Available scoring: {date(minimum)} – {date(maximum)} · All times UTC")

def reset_filters():
    for field in ["factions", "planets", "types", "dates"]:
        st.session_state.pop(f"{field}_{selected}", None)

with st.sidebar.expander("Refine results"):
    st.caption("Leave a selection empty to include everything.")
    factions = st.multiselect("Faction", sorted(df.faction.unique()), key=f"factions_{selected}")
    planets = st.multiselect("Planet", sorted(df.planet.unique()), key=f"planets_{selected}")
    types = st.multiselect("Scoring type", sorted(df.type.unique()), key=f"types_{selected}")
    dates = st.date_input("Dates", (minimum.date(), maximum.date()), min_value=minimum.date(), max_value=maximum.date(), key=f"dates_{selected}")
    st.button("Reset filters", width="stretch", on_click=reset_filters)

filtered = df.copy()
for field, values in [("faction", factions), ("planet", planets), ("type", types)]:
    if values:
        filtered = filtered[filtered[field].isin(values)]
if len(dates) != 2:
    st.info("Choose an end date to complete the date range.")
    st.stop()
filtered = filtered[filtered.logTimestamp.dt.date.between(*dates)]
active = bool(factions or planets or types or dates != (minimum.date(), maximum.date()))
if active:
    st.caption(f"Filtered view · {len(filtered):,} of {len(df):,} scoring records")
if filtered.empty:
    st.info("No scoring matches these filters. Broaden your selection or reset the filters.")
    st.stop()

profile = filtered.assign(earned=filtered.pointValue.clip(lower=0), deductions=filtered.pointValue.clip(upper=0))
faction = profile.groupby("faction").agg(earned=("earned", "sum"), deductions=("deductions", "sum"), net=("pointValue", "sum"), records=("pointValue", "size"))
with st.container(key="headline"):
    cards = st.columns(4)
    for col, name in zip(cards[:2], ["Rebel", "Imperial"]):
        col.metric(f"{name} net points", f"{faction.loc[name, 'net'] if name in faction.index else 0:,.0f}")
    cards[2].metric("Scoring records", f"{len(filtered):,}")
    cards[3].metric("Active planets", str(filtered.planet.nunique()))
st.caption("Net points include gains and deductions. They are not final planetary control scores.")

overview, scoring, worlds, records = st.tabs(["Overview", "Scoring", "Planets", "Records"])
with overview:
    st.subheader("Faction momentum")
    trajectory = st.radio("Display", ["Cumulative points", "Points per day", "Records per day"], horizontal=True)
    daily = grouped_timeseries(filtered, "Daily", "faction", "Activities" if trajectory == "Records per day" else "Points")
    daily = daily.reindex(pd.date_range(daily.index.min(), daily.index.max(), freq="D"))
    if trajectory == "Cumulative points":
        daily = daily.fillna(0).cumsum()
    chart(faction_line_figure(daily, "Records" if trajectory == "Records per day" else "Net points"))
    st.caption("Cumulative values start at the beginning of your selected date range. Gaps in daily views indicate no available records.")
    left,right = st.columns(2)
    with left:
        st.subheader("What drove the scoring")
        totals = grouped_totals(filtered, "type", "faction")
        names = filtered.groupby("type").pointValue.sum().nlargest(8).index
        chart(breakdown_bar_figure(totals[totals.group.isin(names)], "Scoring type"), 400)
    with right:
        st.subheader("Faction contributions")
        summary = faction.reset_index().rename(columns={"faction":"Faction", "earned":"Points gained", "deductions":"Points deducted", "net":"Net points", "records":"Records"})
        table(summary)
        st.caption("Each record is a scoring adjustment; one activity can produce multiple records.")
        st.subheader("Leading scoring type")
        leading = filtered.groupby("type").pointValue.sum().sort_values(ascending=False)
        st.write(f"**{leading.index[0]}**")
        st.caption(f"{leading.iloc[0]:,.0f} net points in this selection")

with scoring:
    st.subheader("How points were scored")
    left,right = st.columns(2)
    primary = left.selectbox("Group by", ["Scoring type", "Planet", "Faction"])
    split = right.selectbox("Compare", ["Faction", "Planet", "Scoring type", "None"])
    dimensions = {"Scoring type":"type", "Planet":"planet", "Faction":"faction", "None":"None"}
    primary, split = dimensions[primary], dimensions[split]
    totals = grouped_totals(filtered, primary, split if split != primary else "None")
    chart(breakdown_bar_figure(totals, primary), max(380, min(900, filtered[primary].nunique()*32)))
    st.caption("Deductions remain visible below zero.")
    pivot = filtered.pivot_table(index="type", columns="faction", values="pointValue", aggfunc="sum", fill_value=0)
    pivot["Net points"] = pivot.sum(axis=1)
    pivot["Records"] = filtered.groupby("type").size()
    table(pivot.sort_values("Net points", ascending=False).reset_index().rename(columns={"type":"Scoring type"}))
    st.subheader("Scoring over time")
    a,b,c = st.columns(3)
    grain = a.selectbox("Interval", ["Daily", "Hourly"])
    measure = b.selectbox("Measure", ["Net points", "Records"])
    series = c.selectbox("Series", ["Scoring type", "Faction"])
    count = st.slider("Scoring types", 3, 12, 6, disabled=series == "Faction")
    top = filtered.groupby("type").pointValue.sum().nlargest(count).index
    series_field = "type" if series == "Scoring type" else "faction"
    subset = filtered[filtered.type.isin(top)] if series_field == "type" else filtered
    timeline = grouped_timeseries(subset, grain, series_field, "Points" if measure == "Net points" else "Activities")
    timeline = timeline.reindex(pd.date_range(timeline.index.min(), timeline.index.max(), freq="D" if grain == "Daily" else "h"))
    fig = px.line(timeline, labels={"value":measure, "index":"", "variable":series}, color_discrete_sequence=px.colors.qualitative.Safe,
        color_discrete_map=FACTION_COLORS if series_field == "faction" else None)
    chart(fig, 430)
    with st.expander("Scoring bonuses"):
        found = False
        for field, title in [("planetModifier", "Planet multiplier"), ("softCapMultiplier", "Soft-cap multiplier")]:
            if field in filtered:
                values = pd.to_numeric(filtered[field], errors="coerce")
                if values.notna().any():
                    found = True
                    st.write(title)
                    table(filtered.assign(value=values).groupby("faction").value.agg(["count", "mean", "min", "max"]).reset_index().rename(columns={"faction":"Faction", "count":"Records", "mean":"Average", "min":"Minimum", "max":"Maximum"}))
        st.caption("Averages weight each scoring record equally; unavailable values are excluded." if found else "Bonus details are not available for this period.")

with worlds:
    st.subheader("The planetary picture")
    chart(breakdown_bar_figure(grouped_totals(filtered, "planet", "faction"), "Planet"), 460)
    planets_table = filtered.pivot_table(index="planet", columns="faction", values="pointValue", aggfunc="sum", fill_value=0)
    planets_table["Net points"] = planets_table.sum(axis=1)
    planets_table["Records"] = filtered.groupby("planet").size()
    table(planets_table.sort_values("Net points", ascending=False).reset_index().rename(columns={"planet":"Planet"}))

with records:
    st.subheader("Explore scoring records")
    st.caption("Source IDs can represent characters or game objects. They are not a count or ranking of players.")
    rows = filtered
    display = rows.sort_values("logTimestamp", ascending=False)[["logTimestamp", "faction", "planet", "type", "pointValue", "source"]].rename(columns={"logTimestamp":"Time (UTC)", "faction":"Faction", "planet":"Planet", "type":"Scoring type", "pointValue":"Points", "source":"Source ID"})
    st.caption(f"{len(display):,} records · newest first")
    table(display)
    st.download_button("Download selected records", display.to_csv(index=False).encode(), file_name=f"gcw-{minimum.date()}-records.csv", mime="text/csv")
    with st.expander("Highest-value records and source totals"):
        table(display.sort_values("Points", ascending=False).head(25))
        table(rows.groupby("source").agg(Records=("pointValue", "size"), Points=("pointValue", "sum")).sort_values("Points", ascending=False).head(25).reset_index().rename(columns={"source":"Source ID"}))

st.divider()
with st.expander("About these numbers"):
    st.write("Explore three periods of GCW scoring. Figures reflect the available records, so periods with different coverage should not be compared as complete cycle totals.")
    if metadata is None:
        st.write("This early period covers February 22–March 27, 2026. Full cycle boundaries and the original timezone are not confirmed; times are presented as UTC.")
    else:
        st.write(f"Cycle dates: {label}. Available scoring runs from {date(minimum)} through {date(maximum)}; coverage across the full cycle is incomplete.")
    st.write("GCW points include gains and deductions. They do not establish final control, personal rewards, or a cycle winner. Latest Shatterpoint uses its own event dates and scoring scale.")
st.caption("SWG Restoration · GCW Observatory")

import json
import pandas as pd
import plotly.express as px
import streamlit as st
from design import header, chart, table, date, FACTION_COLORS


def show_latest_event(path):
    header("Latest Shatterpoint")
    if not path.exists():
        st.info("Event results will appear here when available.")
        return
    event = json.loads(path.read_text())
    title = event["event_type"].removeprefix("shatterpoint_").replace("_", " ").title()
    st.subheader(f"{title} · {event['planet'].title()}")
    st.caption(f"{date(event['start'])} – {date(event['end']) if event['end'] else 'Ongoing'} · All times UTC")
    df = pd.DataFrame(event["results"])
    if df.empty:
        st.info("Results are not yet available for this event.")
        return
    df["logTimestamp"] = pd.to_datetime(df.logTimestamp, utc=True)
    df = df.sort_values("logTimestamp")
    df["Activity"] = df.source.str.replace("_", " ").str.title()
    movement = df.signedImperialMovement
    a,b,c = st.columns(3)
    a.metric("Scoring results", f"{len(df):,}")
    b.metric("Movement toward Rebel", f"{-movement.clip(upper=0).sum():,.0f}")
    c.metric("Movement toward Imperial", f"{movement.clip(lower=0).sum():,.0f}")
    st.caption("Crisis movement has its own scoring scale and is separate from GCW cycle points.")
    overview, detail = st.tabs(["Event overview", "Results"])
    with overview:
        st.subheader("Control through the event")
        fig = px.line(df, x="logTimestamp", y="newImperial", labels={"logTimestamp":"", "newImperial":"Imperial control"}, color_discrete_sequence=[FACTION_COLORS["Imperial"]])
        chart(fig)
        st.caption("Control values at available scoring results. Rising values favor Imperial; falling values favor Rebel. The line connects recorded observations.")
        st.subheader("What moved control")
        grouped = df.assign(Rebel=-movement.clip(upper=0), Imperial=movement.clip(lower=0)).groupby("Activity")[["Rebel", "Imperial"]].sum().reset_index()
        fig = px.bar(grouped.melt(id_vars="Activity", var_name="Faction", value_name="Movement"), x="Movement", y="Activity", color="Faction", orientation="h", barmode="group", color_discrete_map=FACTION_COLORS)
        chart(fig)
        summary = df.groupby("Activity").agg(Results=("appliedMovement", "size"), Movement=("appliedMovement", "sum"), Net=("signedImperialMovement", "sum")).reset_index().rename(columns={"Movement":"Applied movement", "Net":"Net toward Imperial"})
        table(summary)
    with detail:
        display = df[["logTimestamp", "Activity", "requestedMovement", "appliedMovement", "previousImperial", "newImperial", "signedImperialMovement"]].rename(columns={"logTimestamp":"Time (UTC)", "requestedMovement":"Requested movement", "appliedMovement":"Applied movement", "previousImperial":"Control before", "newImperial":"Control after", "signedImperialMovement":"Net toward Imperial"})
        table(display.sort_values("Time (UTC)", ascending=False))
        st.download_button("Download event results", display.to_csv(index=False).encode(), "gcw-latest-shatterpoint.csv", "text/csv")
    with st.expander("Reading this event"):
        st.write("Each result is a scoring change, not necessarily a unique battle or participant. Positive net movement favors Imperial; negative movement favors Rebel. Requested movement is the attempted change; applied movement is the amount applied.")
        st.write("These figures describe the available results, not a definitive winner. Only the latest Shatterpoint is shown because mechanics vary between events.")

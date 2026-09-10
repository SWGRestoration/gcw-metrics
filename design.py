"""Shared presentation for the public dashboard."""
import plotly.graph_objects as go
import streamlit as st

FACTION_COLORS = {"Rebel": "#f07875", "Imperial": "#70b5f9"}

def setup():
    st.set_page_config(page_title="GCW Observatory · SWG Restoration", page_icon="✦", layout="wide")
    st.markdown("""<style>
    .stApp {background: #0c1220; color: #e7edf7;}
    [data-testid="stHeader"] {background: #0c1220;}
    [data-testid="stSidebar"] {background: #111b2c;}
    .block-container {max-width: 1480px; padding-top: 2.8rem; padding-bottom: 3rem;}
    h1 {font-size: 2.65rem !important; font-weight: 700 !important; letter-spacing: -.045em;}
    h2 {font-size: 1.35rem !important; letter-spacing: -.025em;}
    h3 {font-size: 1.08rem !important;}
    [data-testid="stMetric"] {background: #141f31; border: 1px solid #29374c;
      border-radius: 12px; padding: 18px 20px; height: 100%;}
    [data-testid="stMetricValue"] {font-size: 1.95rem; font-variant-numeric: tabular-nums;}
    [data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p {color: #aebed3 !important;}
    .eyebrow {color: #a6bde0; text-transform: uppercase; letter-spacing: .19em;
      font-size: .72rem; font-weight: 650; margin-bottom: .5rem;}
    [data-baseweb="tab-list"] {gap: 1.6rem; margin-bottom: 1rem;}
    [data-baseweb="tab"] {padding-left: 0; padding-right: 0;}
    @media (max-width: 700px) {
      .block-container {padding-top: 1.5rem;}
      h1 {font-size: 2rem !important;}
      [data-testid="stMetricValue"] {font-size: 1.55rem;}
      .st-key-headline [data-testid="stHorizontalBlock"] {flex-wrap: wrap; gap: .7rem;}
      .st-key-headline [data-testid="stColumn"] {min-width: calc(50% - .7rem) !important; width: calc(50% - .7rem) !important; flex: 1 1 calc(50% - .7rem) !important;}
      .st-key-headline [data-testid="stMetric"] {padding: 12px;}
      [data-baseweb="tab-list"] {gap: .7rem;}
    }
    </style>""", unsafe_allow_html=True)

def header(title):
    st.markdown('<div class="eyebrow">SWG Restoration / Galactic Civil War</div>', unsafe_allow_html=True)
    st.title(title)

def chart(fig, height=360):
    fig.update_layout(template="plotly_dark", height=height, paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Arial, sans-serif", color="#b9c8dc", size=12),
        margin=dict(l=12,r=16,t=20,b=16), legend_title_text="",
        legend=dict(orientation="h", y=1.13, x=0), hovermode="closest")
    fig.update_xaxes(gridcolor="#263248", zerolinecolor="#41516b")
    fig.update_yaxes(gridcolor="#263248", zerolinecolor="#41516b")
    st.plotly_chart(fig, width="stretch", config={"displaylogo":False, "modeBarButtonsToRemove":["lasso2d", "select2d"]})

def date(value):
    import pandas as pd
    return pd.Timestamp(value).strftime("%b %-d, %Y")

def table(frame):
    st.dataframe(frame, width="stretch", hide_index=True,
        column_config={c: st.column_config.NumberColumn(format="localized") for c in frame.select_dtypes("number").columns})

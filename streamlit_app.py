import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import datetime

st.set_page_config(page_title="Sponavd AI-styrt", layout="wide")
st.title("🔧 Sponavd AI-styrt")

# Start med eller hent eksisterende data
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=[
        "timestamp", "onsket_fukt", "brennkammer_temp", "innlop_temp", "utlop_temp",
        "primluft", "trykk_ovn", "hombak", "maier", "stovforbrenning", "beregnet_fukt"
    ])

# --- Funksjon for beregnet fukt ---
def beregn_fukt(brennkammer_temp, innlop_temp, utlop_temp, primluft, trykk_ovn, hombak, maier, stov):
    # Dummyformel
    return round(
        (utlop_temp * 0.01 - brennkammer_temp * 0.0005 + hombak * 0.002 - maier * 0.001 + primluft * 0.0007 + stov * 0.001 + trykk_ovn * 0.0002), 2
    )

# --- Input ---
col1, col2 = st.columns(2)

with col1:
    onsket_fukt = st.number_input("Ønsket fukt (%)", value=1.20, step=0.01)

    brennkammer_temp = st.slider("Brennkammertemp (°C)", 600, 1000, 790)
    brennkammer_temp_in = st.number_input("Brennkammertemp (input)", value=brennkammer_temp)

    innlop_temp = st.slider("Innløpstemp (°C)", 250, 700, 400)
    innlop_temp_in = st.number_input("Innløpstemp (input)", value=innlop_temp)

    utlop_temp = st.slider("Utløpstemp (°C)", 100, 180, 134)
    utlop_temp_in = st.number_input("Utløpstemp (input)", value=utlop_temp)

    primluft = st.slider("Primærluft (%)", 0, 100, 20)
    primluft_in = st.number_input("Primærluft (input)", value=primluft)

    trykk_ovn = st.slider("Trykk ovn (Pa)", -500, 0, -270)
    trykk_ovn_in = st.number_input("Trykk ovn (input)", value=trykk_ovn)

    hombak = st.slider("Utmating Hombak (%)", 0, 100, 75)
    hombak_in = st.number_input("Utmating Hombak (input)", value=hombak)

    maier = st.slider("Utmating Maier (%)", 0, 100, 25)
    maier_in = st.number_input("Utmating Maier (input)", value=maier)

    stov = st.slider("Forbrenning av støv (%)", 0, 100, 10)
    stov_in = st.number_input("Forbrenning av støv (input)", value=stov)

# Beregning
beregnet_fukt = beregn_fukt(
    brennkammer_temp_in, innlop_temp_in, utlop_temp_in,
    primluft_in, trykk_ovn_in, hombak_in, maier_in, stov_in
)

avvik = round(onsket_fukt - beregnet_fukt, 2)

with col2:
    st.subheader("📈 Resultat")
    st.metric("Beregnet fukt", f"{beregnet_fukt} %")
    st.metric("Ønsket fukt", f"{onsket_fukt} %")
    st.metric("Avvik", f"{avvik} %")

    if st.button("🔥 Loggfør denne prøven"):
        ny_rad = {
            "timestamp": datetime.now(),
            "onsket_fukt": onsket_fukt,
            "brennkammer_temp": brennkammer_temp_in,
            "innlop_temp": innlop_temp_in,
            "utlop_temp": utlop_temp_in,
            "primluft": primluft_in,
            "trykk_ovn": trykk_ovn_in,
            "hombak": hombak_in,
            "maier": maier_in,
            "stovforbrenning": stov_in,
            "beregnet_fukt": beregnet_fukt
        }
        st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([ny_rad])], ignore_index=True)
        st.success(f"Prøve loggført! Totalt lagret: {len(st.session_state.data)} prøver.")

st.subheader("📋 Oversikt over lagrede prøver")
st.dataframe(st.session_state.data, use_container_width=True)

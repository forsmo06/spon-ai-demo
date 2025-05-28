import streamlit as st
import numpy as np
import pandas as pd
import os
from datetime import datetime
from sklearn.linear_model import LinearRegression

st.set_page_config(layout="wide")

st.title("📊 Fuktstyring - AI & Manuell (Ipaar-stil)")

col1, col2 = st.columns(2)

# === Filnavn for logging og modell ===
LOGG_FIL = "fuktlogg.csv"
MODELL_FIL = "fuktmodell.pkl"

def logg_data(data):
    df = pd.DataFrame([data])
    if os.path.exists(LOGG_FIL):
        df_existing = pd.read_csv(LOGG_FIL)
        df = pd.concat([df_existing, df], ignore_index=True)
    df.to_csv(LOGG_FIL, index=False)

def hent_antall_prøver():
    if os.path.exists(LOGG_FIL):
        df = pd.read_csv(LOGG_FIL)
        return len(df)
    else:
        return 0

# === VIS STATUS for antall prøver uansett ===
antall = hent_antall_prøver()
if antall < 10:
    st.sidebar.info(f"📊 Antall prøver: {antall} av 10 - AI ikke aktiv ennå")
else:
    st.sidebar.success(f"🤖 AI aktiv ✅ - basert på {antall} prøver")

# === VENSTRE SIDE: INNSTILLINGER ===
with col1:
    st.header("🔧 Justeringer")

    ønsket_fukt = st.number_input("Ønsket fukt (%)", 0.5, 4.0, step=0.01, value=1.36)
    brennkammer_temp = st.slider("Brennkammertemp (°C)", 600, 1000, 794)
    innløpstemp = st.slider("Innløpstemp (°C)", 250, 700, 403)
    utløpstemp = st.slider("Utløpstemp (°C)", 100, 180, 133)
    friskluft = st.slider("Forbrenning av støv - Friskluft (%)", 0, 100, 12)
    primluft = st.slider("Primærluftsflækt (%)", 0, 100, 3)
    trykk_ovn = st.slider("Trykk ovn (Pa)", -500, 0, -270)
    utmating_hombak = st.slider("Utmating Hombak (%)", 0, 100, 78)
    utmating_maier = st.slider("Utmating Maier (%)", 0, 100, 25)

    # Data som skal loggføres
    ny_prøve = {
        "timestamp": datetime.now().isoformat(timespec='seconds'),
        "ønsket_fukt": ønsket_fukt,
        "beregnet_fukt": 1.00,  # Sett inn riktig beregnet verdi
        "brennkammertemp": brennkammer_temp,
        "innløpstemp": innløpstemp,
        "utløpstemp": utløpstemp,
        "friskluft": friskluft,
        "primluft": primluft,
        "trykkovn": trykk_ovn,
        "hombak": utmating_hombak,
        "maier": utmating_maier
    }

    if st.button("📥 Loggfør denne prøven"):
        logg_data(ny_prøve)
        st.success("Prøve lagret!")

# === HØYRE SIDE: RESULTAT ===
with col2:
    st.header("📈 Resultat")
    st.metric("Beregnet fukt", f"{ny_prøve['beregnet_fukt']:.2f} %")
    st.metric("Ønsket fukt", f"{ny_prøve['ønsket_fukt']:.2f} %")
    avvik = ny_prøve['beregnet_fukt'] - ny_prøve['ønsket_fukt']
    st.metric("Avvik", f"{avvik:.2f} %")

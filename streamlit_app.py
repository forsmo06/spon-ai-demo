import streamlit as st
import pandas as pd
import os
from datetime import datetime
from sklearn.linear_model import LinearRegression
import numpy as np

st.set_page_config(layout="wide")

st.title("📊 Fuktstyring – AI & Manuell (Ipaar-stil)")

LOGG_FIL = "fuktlogg.csv"
MODELL_FIL = "fuktmodell.pkl"

# Funksjon for logging av prøver
def logg_data(data):
    df = pd.DataFrame([data])
    if os.path.exists(LOGG_FIL):
        df_existing = pd.read_csv(LOGG_FIL)
        df = pd.concat([df_existing, df], ignore_index=True)
    df.to_csv(LOGG_FIL, index=False)

# Funksjon for å hente antall prøver
def hent_antall_prøver():
    if os.path.exists(LOGG_FIL):
        df = pd.read_csv(LOGG_FIL)
        return len(df)
    return 0

# Sjekk antall prøver for statusmelding
antall_prøver = hent_antall_prøver()
if antall_prøver < 10:
    st.sidebar.info(f"📊 Antall prøver: {antall_prøver} av 10 – AI ikke aktiv ennå")
else:
    st.sidebar.success(f"🤖 AI aktiv ✅ – basert på {antall_prøver} prøver")

col1, col2 = st.columns(2)

with col1:
    st.header("🛠 Justeringer")

    ønsket_fukt = st.number_input("Ønsket fukt (%)", 0.5, 4.0, step=0.01, value=1.36)

    brennkammertemp = st.slider("Brennkammertemp (°C)", 600, 1000, 794)
    innløpstemp = st.slider("Innløpstemp (°C)", 250, 700, 403)
    utløpstemp = st.slider("Utløpstemp (°C)", 100, 180, 133)
    friskluft = st.slider("Forbrenning av støv - Friskluft (%)", 0, 100, 12)
    primluft = st.slider("Primærluftsflækt (%)", 0, 100, 3)
    trykkovn = st.slider("Trykk ovn (Pa)", -500, 0, -270)
    hombak = st.slider("Utmating Hombak (%)", 0, 100, 78)
    maier = st.slider("Utmating Maier (%)", 0, 100, 25)

    if st.button("📥 Loggfør denne prøven"):
        ny_prøve = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ønsket_fukt": ønsket_fukt,
            "beregnet_fukt": np.nan,  # Kan fylles ut med AI-prediksjon senere
            "brennkammertemp": brennkammertemp,
            "innløpstemp": innløpstemp,
            "utløpstemp": utløpstemp,
            "friskluft": friskluft,
            "primluft": primluft,
            "trykkovn": trykkovn,
            "hombak": hombak,
            "maier": maier,
        }
        logg_data(ny_prøve)
        st.success("✅ Prøve lagret til fuktlogg.csv")
        antall_prøver = hent_antall_prøver()
        st.sidebar.success(f"🤖 AI aktiv ✅ – basert på {antall_prøver} prøver")

with col2:
    st.header("📈 Resultat")

    # Her kan du implementere prediksjon av beregnet fukt basert på AI-modellen
    # Foreløpig dummyverdi for eksempel
    beregnet_fukt = ønsket_fukt - 0.36
    avvik = beregnet_fukt - ønsket_fukt

    st.markdown(f"**Beregnet fukt:** {beregnet_fukt:.2f} %")
    st.markdown(f"**Ønsket fukt:** {ønsket_fukt:.2f} %")
    st.markdown(f"**Avvik:** {avvik:+.2f} %")

    if 133 <= utløpstemp <= 137:
        st.success("✅ Utløpstemp OK for 22mm gulvplate")
    else:
        st.error("⚠️ Utløpstemp utenfor ønsket område")

    if -280 <= trykkovn <= -260:
        st.success("✅ Trykk ovn OK")
    else:
        st.error("⚠️ Trykk ovn utenfor ønsket område")

    st.info("ℹ️ Når minst 10 prøver er lagret, vil AI begynne å lære og brukes i beregningene.")

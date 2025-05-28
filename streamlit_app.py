import streamlit as st
import pandas as pd
import os
from datetime import datetime
from sklearn.linear_model import LinearRegression
import numpy as np

st.set_page_config(layout="wide")
FILENAME = "fuktlogg.csv"

# Logger ny prøve til CSV, lager ny fil om nødvendig
def lagre_prove(data):
    df_ny = pd.DataFrame([data])
    if os.path.exists(FILENAME):
        df_eks = pd.read_csv(FILENAME)
        df = pd.concat([df_eks, df_ny], ignore_index=True)
    else:
        df = df_ny
    df.to_csv(FILENAME, index=False)
    return len(df)

# Henter antall prøver i loggfilen
def hent_antall():
    if os.path.exists(FILENAME):
        df = pd.read_csv(FILENAME)
        return len(df)
    return 0

# Tren og returner enkel lineær modell hvis minst 10 prøver
def tren_ai_modell():
    if not os.path.exists(FILENAME):
        return None
    df = pd.read_csv(FILENAME)
    if len(df) < 10:
        return None
    X = df[["brennkammer_temp", "innlop_temp", "utlop_temp", "friskluft", "primluft", "trykk_ovn", "hombak", "maier"]]
    y = df["onsket_fukt"]
    model = LinearRegression().fit(X, y)
    return model

st.title("📊 Fuktstyring – AI & Manuell")

antall_prøver = hent_antall()
if antall_prøver < 10:
    st.sidebar.info(f"📊 Antall prøver: {antall_prøver} av 10 – AI ikke aktiv ennå")
else:
    st.sidebar.success(f"🤖 AI aktiv ✅ – basert på {antall_prøver} prøver")

col1, col2 = st.columns(2)

with col1:
    st.header("🛠 Justeringer")

    ønsket_fukt = st.number_input("Ønsket fukt (%)", 0.5, 4.0, step=0.01, value=1.36)

    brennkammer_temp = st.slider("Brennkammertemp (°C)", 600, 1000, 794)
    innlop_temp = st.slider("Innløpstemp (°C)", 250, 700, 403)
    utlop_temp = st.slider("Utløpstemp (°C)", 100, 180, 133)
    friskluft = st.slider("Forbrenning av støv - Friskluft (%)", 0, 100, 12)
    primluft = st.slider("Primærluftsflækt (%)", 0, 100, 3)
    trykk_ovn = st.slider("Trykk ovn (Pa)", -500, 0, -270)
    hombak = st.slider("Utmating Hombak (%)", 0, 100, 78)
    maier = st.slider("Utmating Maier (%)", 0, 100, 25)

    if st.button("📥 Loggfør denne prøven"):
        ny_prøve = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "onsket_fukt": ønsket_fukt,
            "brennkammertemp": brennkammer_temp,
            "innlop_temp": innlop_temp,
            "utlop_temp": utlop_temp,
            "friskluft": friskluft,
            "primluft": primluft,
            "trykk_ovn": trykk_ovn,
            "hombak": hombak,
            "maier": maier,
            "beregnet_fukt": np.nan  # Fylles ut etter AI-prediksjon
        }
        lagre_prove(ny_prøve)
        st.success("✅ Prøve lagret til fuktlogg.csv")

with col2:
    st.header("📈 Resultat")

    model = tren_ai_modell()

    input_data = {
        "brennkammer_temp": brennkammer_temp,
        "innlop_temp": innlop_temp,
        "utlop_temp": utlop_temp,
        "friskluft": friskluft,
        "primluft": primluft,
        "trykk_ovn": trykk_ovn,
        "hombak": hombak,
        "maier": maier,
    }

    if model is not None:
        df_inndata = pd.DataFrame([input_data])
        pred = model.predict(df_inndata)[0]
        beregnet_fukt = round(pred, 2)
    else:
        beregnet_fukt = 1.0  # Dummy verdi før AI er klar

    avvik = beregnet_fukt - ønsket_fukt

    st.metric("🔹 Beregnet fukt", f"{beregnet_fukt:.2f} %")
    st.metric("🎯 Ønsket fukt", f"{ønsket_fukt:.2f} %")
    st.metric("➖ Avvik", f"{avvik:+.2f} %")

    if 133 <= utlop_temp <= 137:
        st.success("✅ Utløpstemp OK for 22mm gulvplate")
    else:
        st.warning("⚠️ Utløpstemp utenfor ønsket område (133–137 °C)")

    if -280 <= trykk_ovn <= -260:
        st.success("✅ Trykk ovn OK")
    else:
        st.warning("⚠️ Trykk ovn utenfor anbefalt område (-280 til -260 Pa)")

    st.info("ℹ️ AI-modellen aktiveres når minst 10 prøver er logget.")

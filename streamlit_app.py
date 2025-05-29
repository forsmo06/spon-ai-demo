import streamlit as st
import pandas as pd
import os
from datetime import datetime
from sklearn.linear_model import LinearRegression

st.set_page_config(layout="wide")
st.title("📊 Fuktstyring – AI & Manuell (Ipaar-stil)")

LOGG_FIL = "fuktlogg.csv"

def logg_data(data):
    df = pd.DataFrame([data])
    if os.path.exists(LOGG_FIL):
        df_existing = pd.read_csv(LOGG_FIL)
        df = pd.concat([df_existing, df], ignore_index=True)
    df.to_csv(LOGG_FIL, index=False)

def tren_model(df):
    nødvendig = ["brennkammertemp", "innløpstemp", "utløpstemp", "primluft", "trykkovn", "hombak", "maier", "ønsket_fukt"]
    for col in nødvendig:
        if col not in df.columns:
            return None
    df = df.dropna(subset=nødvendig)
    if len(df) < 10:
        return None
    X = df[["brennkammertemp", "innløpstemp", "utløpstemp", "primluft", "trykkovn", "hombak", "maier"]]
    y = df["ønsket_fukt"]
    model = LinearRegression()
    model.fit(X, y)
    return model

def beregn_fukt(model, data):
    if model is None:
        return None
    df = pd.DataFrame([data])
    return round(model.predict(df)[0], 2)

col1, col2 = st.columns(2)

with col1:
    st.header("🔧 Justeringer manuelt og via tekst")

    ønsket_fukt = st.number_input("Ønsket fukt (%)", 0.5, 4.0, step=0.01, value=1.36, key="ønsket_fukt")

    brennkammer_slider = st.slider("Brennkammertemp (°C)", 600, 1000, 790, key="brennkammer_slider")
    brennkammer_number = st.number_input("Brennkammertemp (°C) input", 600, 1000, 790, key="brennkammer_number")

    innløp_slider = st.slider("Innløpstemp (°C)", 250, 700, 400, key="innløp_slider")
    innløp_number = st.number_input("Innløpstemp (°C) input", 250, 700, 400, key="innløp_number")

    utløp_slider = st.slider("Utløpstemp (°C)", 100, 180, 135, key="utløp_slider")
    utløp_number = st.number_input("Utløpstemp (°C) input", 100, 180, 135, key="utløp_number")

    primluft_slider = st.slider("Primærluft (%)", 0, 100, 3, key="primluft_slider")
    primluft_number = st.number_input("Primærluft (%) input", 0, 100, 3, key="primluft_number")

    trykkovn_slider = st.slider("Trykk ovn (Pa)", -500, 0, -270, key="trykkovn_slider")
    trykkovn_number = st.number_input("Trykk ovn (Pa) input", -500, 0, -270, key="trykkovn_number")

    hombak_slider = st.slider("Utmating Hombak (%)", 0, 100, 78, key="hombak_slider")
    hombak_number = st.number_input("Utmating Hombak (%) input", 0, 100, 78, key="hombak_number")

    maier_slider = st.slider("Utmating Maier (%)", 0, 100, 25, key="maier_slider")
    maier_number = st.number_input("Utmating Maier (%) input", 0, 100, 25, key="maier_number")

    # Sync slider and number input values manually:
    if brennkammer_slider != brennkammer_number:
        st.session_state.brennkammer_slider = brennkammer_number
    if innløp_slider != innløp_number:
        st.session_state.innløp_slider = innløp_number
    if utløp_slider != utløp_number:
        st.session_state.utløp_slider = utløp_number
    if primluft_slider != primluft_number:
        st.session_state.primluft_slider = primluft_number
    if trykkovn_slider != trykkovn_number:
        st.session_state.trykkovn_slider = trykkovn_number
    if hombak_slider != hombak_number:
        st.session_state.hombak_slider = hombak_number
    if maier_slider != maier_number:
        st.session_state.maier_slider = maier_number

with col2:
    st.header("📈 Resultat")

    input_data = {
        "brennkammertemp": st.session_state.brennkammer_slider,
        "innløpstemp": st.session_state.innløp_slider,
        "utløpstemp": st.session_state.utløp_slider,
        "primluft": st.session_state.primluft_slider,
        "trykkovn": st.session_state.trykkovn_slider,
        "hombak": st.session_state.hombak_slider,
        "maier": st.session_state.maier_slider
    }

    if os.path.exists(LOGG_FIL):
        df_logg = pd.read_csv(LOGG_FIL)
    else:
        df_logg = pd.DataFrame()

    model = tren_model(df_logg)
    beregnet_fukt = beregn_fukt(model, input_data)
    beregnet_fukt = beregnet_fukt if beregnet_fukt is not None else 0

    avvik = round(beregnet_fukt - ønsket_fukt, 2)

    st.metric("🔹 Beregnet fukt", f"{beregnet_fukt:.2f} %")
    st.metric("🎯 Ønsket fukt", f"{ønsket_fukt:.2f} %")
    st.metric("➖ Avvik", f"{avvik:+.2f} %")

    if st.button("📥 Loggfør denne prøven"):
        data_logg = {
            "timestamp": datetime.now().isoformat(),
            "ønsket_fukt": ønsket_fukt,
            "brennkammertemp": input_data["brennkammertemp"],
            "innløpstemp": input_data["innløpstemp"],
            "utløpstemp": input_data["utløpstemp"],
            "primluft": input_data["primluft"],
            "trykkovn": input_data["trykkovn"],
            "hombak": input_data["hombak"],
            "maier": input_data["maier"],
            "beregnet_fukt": beregnet_fukt
        }
        logg_data(data_logg)
        st.success("✅ Prøve lagret!")

    st.write("---")
    st.subheader("Oversikt over lagrede prøver")

    if not df_logg.empty:
        st.dataframe(df_logg)
    else:
        st.write("Ingen prøver loggført ennå.")

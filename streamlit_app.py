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
    # Sjekk at alle nødvendige kolonner finnes
    nødvendig = ["brennkammertemp", "innløpstemp", "utløpstemp", "primluft", "trykkovn", "hombak", "maier", "ønsket_fukt"]
    for col in nødvendig:
        if col not in df.columns:
            st.error(f"Mangler kolonne: {col}")
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
    st.header("🔧 Justeringer")

    ønsket_fukt = st.number_input("Ønsket fukt (%)", 0.5, 4.0, step=0.01, value=1.36)
    brennkammer = st.slider("Brennkammertemp (°C)", 600, 1000, 790)
    innløp = st.slider("Innløpstemp (°C)", 250, 700, 400)
    utløp = st.slider("Utløpstemp (°C)", 100, 180, 135)
    primluft = st.slider("Primærluft (%)", 0, 100, 3)
    trykkovn = st.slider("Trykk ovn (Pa)", -500, 0, -270)
    hombak = st.slider("Utmating Hombak (%)", 0, 100, 78)
    maier = st.slider("Utmating Maier (%)", 0, 100, 25)

with col2:
    st.header("📈 Resultat")

    input_data = {
        "brennkammertemp": brennkammer,
        "innløpstemp": innløp,
        "utløpstemp": utløp,
        "primluft": primluft,
        "trykkovn": trykkovn,
        "hombak": hombak,
        "maier": maier
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
            "brennkammertemp": brennkammer,
            "innløpstemp": innløp,
            "utløpstemp": utløp,
            "primluft": primluft,
            "trykkovn": trykkovn,
            "hombak": hombak,
            "maier": maier,
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

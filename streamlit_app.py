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

def synced_slider_number(key, label, min_val, max_val, step, format_str):
    # Initialiser state hvis ikke finnes
    if key not in st.session_state:
        st.session_state[key] = min_val

    col1, col2 = st.columns([3, 1])
    with col1:
        val = st.slider(label, min_val, max_val, st.session_state[key], step=step, key=key+"_slider")
    with col2:
        val_input = st.number_input(label + " (input)", min_val, max_val, st.session_state[key], step=step, format=format_str, key=key+"_number")

    # Sync session_state
    # Hvis slider ble endret:
    if val != st.session_state[key]:
        st.session_state[key] = val
    # Hvis input ble endret:
    elif val_input != st.session_state[key]:
        st.session_state[key] = val_input

    return st.session_state[key]

col1, col2 = st.columns(2)

with col1:
    st.header("🔧 Justeringer manuelt og via tekst")

    ønsket_fukt = st.number_input("Ønsket fukt (%)", 0.5, 4.0, step=0.01, value=1.36, key="ønsket_fukt")

    brennkammer = synced_slider_number("brennkammer", "Brennkammertemp (°C)", 600, 1000, 1, "%d")
    innløp = synced_slider_number("innløp", "Innløpstemp (°C)", 250, 700, 1, "%d")
    utløp = synced_slider_number("utløp", "Utløpstemp (°C)", 100, 180, 1, "%d")
    primluft = synced_slider_number("primluft", "Primærluft (%)", 0, 100, 1, "%d")
    trykkovn = synced_slider_number("trykkovn", "Trykk ovn (Pa)", -500, 0, 1, "%d")
    hombak = synced_slider_number("hombak", "Utmating Hombak (%)", 0, 100, 1, "%d")
    maier = synced_slider_number("maier", "Utmating Maier (%)", 0, 100, 1, "%d")

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

import streamlit as st
import pandas as pd
import os
from datetime import datetime
from sklearn.linear_model import LinearRegression
import numpy as np

FILENAME = "fuktlogg.csv"

def lagre_prove(data):
    df_ny = pd.DataFrame([data])
    if os.path.exists(FILENAME):
        df_eks = pd.read_csv(FILENAME)
        df = pd.concat([df_eks, df_ny], ignore_index=True)
    else:
        df = df_ny
    df.to_csv(FILENAME, index=False)
    return df

def tren_model(df):
    map_kolonner = {
        "brennkammer_temp": "brennkammer_temp",
        "innlop_temp": "innlop_temp",
        "utlop_temp": "utlop_temp",
        "friskluft": "friskluft",
        "primluft": "primluft",
        "trykk_ovn": "trykk_ovn",
        "hombak": "hombak",
        "maier": "maier"
    }

    nødvendige_kolonner = []
    for k in map_kolonner.keys():
        if k in df.columns:
            nødvendige_kolonner.append(k)

    if not nødvendige_kolonner:
        st.error("Ingen gyldige kolonner for trening funnet i data.")
        return None

    X = df[nødvendige_kolonner].copy()
    X.rename(columns=map_kolonner, inplace=True)

    if "beregnet_fukt" not in df.columns:
        st.error("Data mangler kolonnen 'beregnet_fukt'. Kan ikke trene modellen.")
        return None

    y = df["beregnet_fukt"]

    mask = X.notnull().all(axis=1) & y.notnull()
    X = X.loc[mask]
    y = y.loc[mask]

    if len(X) == 0:
        st.error("Ingen gyldige data igjen etter fjerning av manglende verdier.")
        return None

    model = LinearRegression()
    model.fit(X, y)
    return model

def beregn_fukt(model, input_data):
    if model is None:
        return np.nan
    X = pd.DataFrame([input_data])
    pred = model.predict(X)[0]
    return round(pred, 2)

def nullstill_logg():
    if os.path.exists(FILENAME):
        os.remove(FILENAME)

st.title("Logging og AI-beregning av fuktprøver")

timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
onsket_fukt = st.number_input("Ønsket fukt (%)", min_value=0.0, max_value=100.0, value=1.36, format="%.2f")
beregnet_fukt = st.number_input("Beregnet fukt (%)", min_value=0.0, max_value=100.0, value=1.25, format="%.2f")
brennkammer_temp = st.number_input("Brennkammertemp (°C)", value=790)
innlop_temp = st.number_input("Innløpstemp (°C)", value=400)
utlop_temp = st.number_input("Utløpstemp (°C)", value=135)
friskluft = st.number_input("Friskluft (%)", value=12)
primluft = st.number_input("Primærluft (%)", value=3)
trykk_ovn = st.number_input("Trykk ovn (Pa)", value=-270)
hombak = st.number_input("Utmating Hombak (%)", value=78)
maier = st.number_input("Utmating Maier (%)", value=25)

if st.button("Loggfør prøve"):
    ny_prove = {
        "timestamp": timestamp,
        "onsket_fukt": onsket_fukt,
        "beregnet_fukt": beregnet_fukt,
        "brennkammer_temp": brennkammer_temp,
        "innlop_temp": innlop_temp,
        "utlop_temp": utlop_temp,
        "friskluft": friskluft,
        "primluft": primluft,
        "trykk_ovn": trykk_ovn,
        "hombak": hombak,
        "maier": maier
    }
    df = lagre_prove(ny_prove)
    st.success("Prøve lagret!")
else:
    if os.path.exists(FILENAME):
        df = pd.read_csv(FILENAME)
    else:
        df = pd.DataFrame()

model = tren_model(df) if not df.empty else None

input_for_pred = {
    "brennkammer_temp": brennkammer_temp,
    "innlop_temp": innlop_temp,
    "utlop_temp": utlop_temp,
    "friskluft": friskluft,
    "primluft": primluft,
    "trykk_ovn": trykk_ovn,
    "hombak": hombak,
    "maier": maier
}

ai_fukt = beregn_fukt(model, input_for_pred)

st.markdown("---")
st.subheader("Fuktighetsoversikt")
col1, col2, col3 = st.columns(3)

col1.metric("Ønsket fuktighet", f"{onsket_fukt:.2f} %")
col2.metric("Beregnet fuktighet", f"{beregnet_fukt:.2f} %")
if not np.isnan(ai_fukt):
    col3.metric("AI beregnet fuktighet", f"{ai_fukt:.2f} %")
else:
    col3.write("AI-modellen er ikke klar")

st.markdown("---")

if not df.empty:
    st.subheader("Oversikt over lagrede prøver")
    st.dataframe(df)

if st.button("Nullstill logg (slett alle prøver)"):
    nullstill_logg()
    st.experimental_rerun()

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
    return len(df)

def les_prøver():
    if os.path.exists(FILENAME):
        return pd.read_csv(FILENAME)
    else:
        return pd.DataFrame()

def tren_model(df):
    x = df[["brennkammertemp", "innløpstemp", "utløpstemp", "friskluft", "primluft", "trykkovn", "hombak", "maier"]]
    y = df["beregnet_fukt"]
    model = LinearRegression()
    model.fit(x, y)
    return model

def prediker_fukt(model, prøve):
    x_new = np.array([[prøve["brennkammertemp"], prøve["innløpstemp"], prøve["utløpstemp"],
                       prøve["friskluft"], prøve["primluft"], prøve["trykkovn"], prøve["hombak"], prøve["maier"]]])
    pred = model.predict(x_new)
    return pred[0]

def nullstill_logg():
    if os.path.exists(FILENAME):
        os.remove(FILENAME)

st.title("Logging av fuktprøver med AI")

# Les inn eksisterende prøver
df = les_prøver()

st.sidebar.write(f"Antall prøver: {len(df)}")

if st.sidebar.button("Nullstill logg (slett alle prøver)"):
    nullstill_logg()
    st.experimental_rerun()

# Inputfelter
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
ønsket_fukt = st.number_input("Ønsket fukt (%)", min_value=0.0, format="%.2f", value=1.36)
beregnet_fukt = st.number_input("Beregnet fukt (%)", min_value=0.0, format="%.2f", value=1.25)
brennkammertemp = st.number_input("Brennkammertemp (°C)", value=790)
innløpstemp = st.number_input("Innløpstemp (°C)", value=400)
utløpstemp = st.number_input("Utløpstemp (°C)", value=135)
friskluft = st.number_input("Friskluft (%)", value=12)
primluft = st.number_input("Primluft (%)", value=3)
trykkovn = st.number_input("Trykk ovn (Pa)", value=-270)
hombak = st.number_input("Utmating Hombak (%)", value=78)
maier = st.number_input("Utmating Maier (%)", value=25)

if st.button("Loggfør prøve"):
    prøve = {
        "timestamp": timestamp,
        "ønsket_fukt": ønsket_fukt,
        "beregnet_fukt": beregnet_fukt,
        "brennkammertemp": brennkammertemp,
        "innløpstemp": innløpstemp,
        "utløpstemp": utløpstemp,
        "friskluft": friskluft,
        "primluft": primluft,
        "trykkovn": trykkovn,
        "hombak": hombak,
        "maier": maier
    }
    antall = lagre_prove(prøve)
    st.success(f"Prøve loggført! Totalt lagret: {antall}")

# Hvis vi har minst 10 prøver, tren AI-modell
if len(df) >= 10:
    model = tren_model(df)
    est_fukt = prediker_fukt(model, {
        "brennkammertemp": brennkammertemp,
        "innløpstemp": innløpstemp,
        "utløpstemp": utløpstemp,
        "friskluft": friskluft,
        "primluft": primluft,
        "trykkovn": trykkovn,
        "hombak": hombak,
        "maier": maier
    })
    st.info(f"AI estimert fuktighet: {est_fukt:.2f} %")

# Vis tabell med alle prøver
st.subheader("Oversikt over lagrede prøver")
if len(df) > 0:
    st.dataframe(df)
else:
    st.write("Ingen prøver lagret enda.")

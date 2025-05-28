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

def tren_model(df):
    # Velg inputvariabler og target
    X = df[["brennkammertemp", "innløpstemp", "utløpstemp", "friskluft", "primluft", "trykkovn", "hombak", "maier"]]
    y = df["beregnet_fukt"]
    model = LinearRegression()
    model.fit(X, y)
    return model

def prediker_fukt(model, input_data):
    X = np.array([input_data]).reshape(1, -1)
    return model.predict(X)[0]

st.title("Logging av fuktprøver med AI-prediksjon")

# Inputfelter
timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
ønsket_fukt = st.number_input("Ønsket fukt (%)", min_value=0.0, format="%.2f", value=1.36)
beregnet_fukt = st.number_input("Beregnet fukt (%)", min_value=0.0, format="%.2f", value=1.25)
brennkammertemp = st.number_input("Brennkammertemp (°C)", value=790)
innløpstemp = st.number_input("Innløpstemp (°C)", value=400)
utløpstemp = st.number_input("Utløpstemp (°C)", value=135)
friskluft = st.number_input("Friskluft (%)", value=12)
primluft = st.number_input("Primærluft (%)", value=3)
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
    st.success(f"Prøve logget! Totalt antall prøver: {antall}")

# Last inn data og tren modell om nok prøver
if os.path.exists(FILENAME):
    df = pd.read_csv(FILENAME)
    if len(df) >= 10:
        model = tren_model(df)
        input_data = [brennkammertemp, innløpstemp, utløpstemp, friskluft, primluft, trykkovn, hombak, maier]
        pred_fukt = prediker_fukt(model, input_data)
        avvik = pred_fukt - ønsket_fukt
        st.markdown(f"## AI-prediksjon")
        st.write(f"Predikert fuktighet: **{pred_fukt:.2f} %**")
        st.write(f"Avvik fra ønsket fukt: **{avvik:+.2f} %**")

        # Enkel anbefaling basert på avvik
        if avvik > 0.05:
            st.warning("Fuktigheten er høyere enn ønsket. Vurder å redusere temperatur eller mating.")
        elif avvik < -0.05:
            st.warning("Fuktigheten er lavere enn ønsket. Vurder å øke temperatur eller mating.")
        else:
            st.success("Fuktigheten er innenfor ønsket område.")
    else:
        st.info(f"AI-modellen aktiveres når minst 10 prøver er logget. Nåværende antall: {len(df)}")
else:
    st.info("Ingen prøver logget enda.")

# Vis oversikt over alle prøver nederst
if os.path.exists(FILENAME):
    df = pd.read_csv(FILENAME)
    st.markdown("### Oversikt over alle loggførte prøver")
    st.dataframe(df)

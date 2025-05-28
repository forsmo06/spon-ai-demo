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
    # Sørg for at alle nødvendige kolonner finnes i df
    forventede_kolonner = ["brennkammertemp", "innløpstemp", "utløpstemp", "friskluft", "primluft", "trykkovn", "hombak", "maier"]
    for kol in forventede_kolonner:
        if kol not in df.columns:
            st.error(f"Data mangler kolonnen '{kol}'. Kan ikke trene modellen.")
            return None
    
    X = df[forventede_kolonner]
    y = df["beregnet_fukt"]
    model = LinearRegression()
    model.fit(X, y)
    return model

st.title("Logging og beregning av fuktprøver")

# Last inn tidligere prøver hvis mulig
if os.path.exists(FILENAME):
    df = pd.read_csv(FILENAME)
else:
    df = pd.DataFrame(columns=[
        "timestamp", "ønsket_fukt", "beregnet_fukt", "brennkammertemp", "innløpstemp",
        "utløpstemp", "friskluft", "primluft", "trykkovn", "hombak", "maier"
    ])

# Inputfelt for ny prøve
with st.form("ny_prøve"):
    ønsket_fukt = st.number_input("Ønsket fukt (%)", min_value=0.0, format="%.2f")
    beregnet_fukt = st.number_input("Beregnet fukt (%)", min_value=0.0, format="%.2f")
    brennkammertemp = st.number_input("Brennkammertemp (°C)", value=790)
    innløpstemp = st.number_input("Innløpstemp (°C)", value=400)
    utløpstemp = st.number_input("Utløpstemp (°C)", value=135)
    friskluft = st.number_input("Friskluft (%)", value=12)
    primluft = st.number_input("Primærluft (%)", value=3)
    trykkovn = st.number_input("Trykk ovn (Pa)", value=-270)
    hombak = st.number_input("Utmating Hombak (%)", value=78)
    maier = st.number_input("Utmating Maier (%)", value=25)
    submit = st.form_submit_button("Loggfør prøve")

if submit:
    ny_prove = {
        "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "ønsket_fukt": ønsket_fukt,
        "beregnet_fukt": beregnet_fukt,
        "brennkammertemp": brennkammertemp,
        "innløpstemp": innløpstemp,
        "utløpstemp": utløpstemp,
        "friskluft": friskluft,
        "primluft": primluft,
        "trykkovn": trykkovn,
        "hombak": hombak,
        "maier": maier,
    }
    antall = lagre_prove(ny_prove)
    st.success(f"Prøve logget! Totalt antall prøver: {antall}")

# Vis tidligere prøver i tabell
st.subheader("Oversikt over lagrede prøver")
st.dataframe(df)

# Tren og vis AI-modell hvis nok data
if len(df) >= 10:
    model = tren_model(df)
    if model:
        # Lag input fra nåværende sliderverdier for prediksjon
        input_data = np.array([[brennkammertemp, innløpstemp, utløpstemp, friskluft, primluft, trykkovn, hombak, maier]])
        pred_fukt = model.predict(input_data)[0]
        st.subheader("AI Beregning")
        st.write(f"Basert på modellen: Beregnet fukt bør være ca. {pred_fukt:.2f} %")
else:
    st.info("AI-modellen aktiveres når minst 10 prøver er logget.")

# Nullstillingsknapp
if st.button("Nullstill logg (slett alle prøver)"):
    if os.path.exists(FILENAME):
        os.remove(FILENAME)
    st.success("Logg slettet! Oppdater siden for å se endringene.")

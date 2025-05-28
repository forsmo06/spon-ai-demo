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
    # Sjekk hvilke kolonner vi har
    st.write("Kolonner i data:", list(df.columns))

    # Map faktiske kolonnenavn i CSV til variabelnavn som brukes i modellen
    map_kolonner = {
        "brennkammertemp": "brennkammertemp",
        "brennkammertemp ": "brennkammertemp",  # mulig trailing space
        "innløpstemp": "innlop_temp",
        "innlop_temp": "innlop_temp",
        "utløpstemp": "utlop_temp",
        "utlop_temp": "utlop_temp",
        "friskluft": "friskluft",
        "primluft": "primluft",
        "trykkovn": "trykk_ovn",
        "trykk_ovn": "trykk_ovn",
        "hombak": "hombak",
        "maier": "maier"
    }

    # Lag liste med faktiske kolonnenavn vi trenger
    nødvendige_kolonner = []
    for k in map_kolonner.keys():
        if k in df.columns:
            nødvendige_kolonner.append(k)

    # Sjekk at alle nødvendige finnes
    if not nødvendige_kolonner:
        st.error("Ingen gyldige kolonner for trening funnet i data.")
        return None

    # Lag DataFrame med riktige kolonner og gi dem riktig navn
    X = df[nødvendige_kolonner].copy()
    X.rename(columns=map_kolonner, inplace=True)

    # Sjekk at beregnet_fukt finnes
    if "beregnet_fukt" not in df.columns:
        st.error("Data mangler kolonnen 'beregnet_fukt'. Kan ikke trene modellen.")
        return None

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
        "timestamp", "onsket_fukt", "beregnet_fukt", "brennkammertemp", "innlop_temp",
        "utlop_temp", "friskluft", "primluft", "trykk_ovn", "hombak", "maier"
    ])

# Inputfelt for ny prøve
with st.form("ny_prove"):
    onsket_fukt = st.number_input("Ønsket fukt (%)", min_value=0.0, format="%.2f")
    beregnet_fukt = st.number_input("Beregnet fukt (%)", min_value=0.0, format="%.2f")
    brennkammertemp = st.number_input("Brennkammertemp (°C)", value=790)
    innlop_temp = st.number_input("Innløpstemp (°C)", value=400)
    utlop_temp = st.number_input("Utløpstemp (°C)", value=135)
    friskluft = st.number_input("Friskluft (%)", value=12)
    primluft = st.number_input("Primærluft (%)", value=3)
    trykk_ovn = st.number_input("Trykk ovn (Pa)", value=-270)
    hombak = st.number_input("Utmating Hombak (%)", value=78)
    maier = st.number_input("Utmating Maier (%)", value=25)
    submit = st.form_submit_button("Loggfør prøve")

if submit:
    ny_prove = {
        "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "onsket_fukt": onsket_fukt,
        "beregnet_fukt": beregnet_fukt,
        "brennkammertemp": brennkammertemp,
        "innlop_temp": innlop_temp,
        "utlop_temp": utlop_temp,
        "friskluft": friskluft,
        "primluft": primluft,
        "trykk_ovn": trykk_ovn,
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
        input_data = np.array([[brennkammertemp, innlop_temp, utlop_temp, friskluft, primluft, trykk_ovn, hombak, maier]])
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

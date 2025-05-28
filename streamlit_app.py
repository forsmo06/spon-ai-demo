import streamlit as st
import pandas as pd
import os
from datetime import datetime

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

st.title("Logging av fuktprøver")

# Inputfelter for prøvedata
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
        "maier": maier,
    }
    totalt = lagre_prove(prøve)
    st.success(f"Prøve lagret! Totalt antall prøver: {totalt}")

# Vis antall lagrede prøver
if os.path.exists(FILENAME):
    df_vis = pd.read_csv(FILENAME)
    st.write(f"Totalt antall prøver i loggen: {len(df_vis)}")
else:
    st.write("Ingen prøver lagret enda.")

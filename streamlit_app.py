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

# Inputfelt for prøvedata
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
onsket_fukt = st.number_input("Ønsket fukt (%)", min_value=0.0, format="%.2f", value=1.36)
beregnet_fukt = st.number_input("Beregnet fukt (%)", min_value=0.0, format="%.2f", value=1.24)
brennkammertemp = st.number_input("Brennkammertemp (°C)", value=790)
innlopstemp = st.number_input("Innløpstemp (°C)", value=400)
utlopstemp = st.number_input("Utløpstemp (°C)", value=135)
friskluft = st.number_input("Friskluft (%)", value=12)
primluft = st.number_input("Primærluft (%)", value=3)
trykkovn = st.number_input("Trykk ovn (Pa)", value=-270)
hombak = st.number_input("Utmatning Hombak (%)", value=78)
maier = st.number_input("Utmatning Maier (%)", value=25)

if st.button("Loggfør prøve"):
    prove = {
        "timestamp": timestamp,
        "onsket_fukt": onsket_fukt,
        "beregnet_fukt": beregnet_fukt,
        "brennkammertemp": brennkammertemp,
        "innlopstemp": innlopstemp,
        "utlopstemp": utlopstemp,
        "friskluft": friskluft,
        "primluft": primluft,
        "trykkovn": trykkovn,
        "hombak": hombak,
        "maier": maier,
    }
    antall = lagre_prove(prove)
    st.success(f"Prøve lagret! Totalt {antall} prøver i loggen.")

# Vis tabell med lagrede prøver
if os.path.exists(FILENAME):
    df = pd.read_csv(FILENAME)
    st.subheader("Oversikt over lagrede prøver")
    st.dataframe(df)
else:
    st.info("Ingen prøver logget enda.")

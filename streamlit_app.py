import streamlit as st
import pandas as pd
import os
from datetime import datetime

LOGG_FIL = "fuktlogg.csv"

def lagre_prøve(data):
    # Hvis fil ikke eksisterer, oppretter vi ny DataFrame med kolonner
    if not os.path.exists(LOGG_FIL):
        df = pd.DataFrame(columns=data.keys())
        df = df.append(data, ignore_index=True)
        df.to_csv(LOGG_FIL, index=False)
    else:
        df = pd.read_csv(LOGG_FIL)
        df = df.append(data, ignore_index=True)
        df.to_csv(LOGG_FIL, index=False)

def hent_antall():
    if os.path.exists(LOGG_FIL):
        df = pd.read_csv(LOGG_FIL)
        return len(df)
    return 0

st.title("Ny Fuktlogg - Logger prøver til CSV")

antall = hent_antall()
st.write(f"Antall prøver lagret: {antall}")

ønsket_fukt = st.number_input("Ønsket fukt (%)", min_value=0.0, max_value=10.0, value=1.36, step=0.01)
brennkammertemp = st.slider("Brennkammertemp (°C)", 600, 1000, 794)
innløpstemp = st.number_input("Innløpstemp (°C)", 0, 1000, 403)
utløpstemp = st.number_input("Utløpstemp (°C)", 0, 1000, 133)
friskluft = st.number_input("Friskluft (%)", 0, 100, 12)
primluft = st.number_input("Primærluft (%)", 0, 100, 3)
trykkovn = st.number_input("Trykk ovn (Pa)", -500, 0, -270)
hombak = st.number_input("Utmating Hombak (%)", 0, 100, 78)
maier = st.number_input("Utmating Maier (%)", 0, 100, 25)

if st.button("Loggfør prøve"):
    prøve = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ønsket_fukt": ønsket_fukt,
        "brennkammertemp": brennkammertemp,
        "innløpstemp": innløpstemp,
        "utløpstemp": utløpstemp,
        "friskluft": friskluft,
        "primluft": primluft,
        "trykkovn": trykkovn,
        "hombak": hombak,
        "maier": maier,
    }
    lagre_prøve(prøve)
    st.success("Prøve lagret!")
    antall = hent_antall()
    st.write(f"Antall prøver lagret: {antall}")

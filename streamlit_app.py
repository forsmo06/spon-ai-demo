import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Filnavn for loggfilen
LOGG_FIL = "fuktlogg.csv"

def logg_data(data):
    df = pd.DataFrame([data])
    if os.path.exists(LOGG_FIL):
        df_existing = pd.read_csv(LOGG_FIL)
        df = pd.concat([df_existing, df], ignore_index=True)
    df.to_csv(LOGG_FIL, index=False)

def hent_antall_prøver():
    if os.path.exists(LOGG_FIL):
        df = pd.read_csv(LOGG_FIL)
        return len(df)
    return 0

st.title("📊 Test logging til CSV")

antall_prøver = hent_antall_prøver()
st.write(f"Antall prøver lagret: {antall_prøver}")

# Inputfelt
ønsket_fukt = st.number_input("Ønsket fukt (%)", min_value=0.0, max_value=10.0, value=1.36, step=0.01)
brennkammertemp = st.slider("Brennkammertemp (°C)", 600, 1000, 794)

if st.button("Loggfør prøve"):
    ny_prøve = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ønsket_fukt": ønsket_fukt,
        "brennkammertemp": brennkammertemp,
        # Du kan legge til flere felter her etter behov
    }
    logg_data(ny_prøve)
    st.success("Prøve lagret!")
    antall_prøver = hent_antall_prøver()
    st.write(f"Antall prøver lagret: {antall_prøver}")

import streamlit as st
import pandas as pd
import os
from datetime import datetime

LOGG_FIL = "fuktlogg.csv"

def logg_data(data):
    df_ny = pd.DataFrame([data])
    if os.path.exists(LOGG_FIL):
        df_eksisterende = pd.read_csv(LOGG_FIL)
        df_oppdatert = pd.concat([df_eksisterende, df_ny], ignore_index=True)
    else:
        df_oppdatert = df_ny
    df_oppdatert.to_csv(LOGG_FIL, index=False)

st.title("Test logging til CSV")

# Les inn eksisterende prøver for å vise antall
if os.path.exists(LOGG_FIL):
    df_logg = pd.read_csv(LOGG_FIL)
    antall_prøver = len(df_logg)
else:
    antall_prøver = 0

st.write(f"Antall prøver lagret: {antall_prøver}")

# Inputfelt for data
ønsket_fukt = st.number_input("Ønsket fukt (%)", 0.5, 4.0, step=0.01, value=1.36)
brennkammertemp = st.slider("Brennkammertemp (°C)", 600, 1000, 794)

if st.button("Loggfør prøve"):
    ny_prøve = {
        "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "ønsket_fukt": ønsket_fukt,
        "brennkammertemp": brennkammertemp,
        # Legg til flere felter her hvis du vil
    }
    logg_data(ny_prøve)
    st.success("Prøve lagret!")
    st.experimental_rerun()  # Oppdater siden for å vise nytt antall prøver

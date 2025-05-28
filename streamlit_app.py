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

# Vi leser filen først én gang
if os.path.exists(LOGG_FIL):
    df_logg = pd.read_csv(LOGG_FIL)
else:
    df_logg = pd.DataFrame()

# Initialt antall prøver
antall_prøver = len(df_logg)
st.write(f"Antall prøver lagret: {antall_prøver}")

ønsket_fukt = st.number_input("Ønsket fukt (%)", 0.5, 4.0, step=0.01, value=1.36)
brennkammertemp = st.slider("Brennkammertemp (°C)", 600, 1000, 794)

if st.button("Loggfør prøve"):
    ny_prøve = {
        "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "ønsket_fukt": ønsket_fukt,
        "brennkammertemp": brennkammertemp,
    }
    logg_data(ny_prøve)
    st.success("Prøve lagret!")

    # Oppdater antallet ved å legge til 1, slik at bruker ser umiddelbar feedback
    antall_prøver += 1
    st.write(f"Antall prøver lagret: {antall_prøver}")

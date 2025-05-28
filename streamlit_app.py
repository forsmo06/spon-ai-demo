import streamlit as st
import pandas as pd
import os
from datetime import datetime

LOGG_FIL = "fuktlogg.csv"

def logg_data(data):
    df = pd.DataFrame([data])
    if os.path.exists(LOGG_FIL):
        df_existing = pd.read_csv(LOGG_FIL)
        df = pd.concat([df_existing, df], ignore_index=True)
    df.to_csv(LOGG_FIL, index=False)

st.title("Test logging til CSV")

# Vis hvor appen kjører fra
st.write("App kjøres fra:", os.getcwd())

# Vis antall lagrede prøver
if os.path.exists(LOGG_FIL):
    df = pd.read_csv(LOGG_FIL)
    st.write(f"Antall prøver lagret: {len(df)}")
else:
    st.write("Ingen prøver lagret enda.")

# Enkel input for å logge en ny prøve
ønsket_fukt = st.number_input("Ønsket fukt (%)", min_value=0.5, max_value=5.0, value=1.36, step=0.01)
brennkammertemp = st.slider("Brennkammertemp (°C)", 600, 1000, 794)

if st.button("Loggfør prøve"):
    data = {
        "timestamp": datetime.now().isoformat(),
        "ønsket_fukt": ønsket_fukt,
        "brennkammertemp": brennkammertemp
    }
    logg_data(data)
    st.success("Prøve lagret!")

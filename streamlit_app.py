import streamlit as st
import pandas as pd
import os
from datetime import datetime

FILENAME = "fuktlogg.csv"

def lagre_prove(data):
    # Hvis fil finnes, les den inn, ellers lag tom DF med kolonner
    if os.path.exists(FILENAME):
        df = pd.read_csv(FILENAME)
    else:
        df = pd.DataFrame(columns=data.keys())
    # Legg til ny prøve som rad
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    # Lagre tilbake til CSV
    df.to_csv(FILENAME, index=False)
    return df

def les_prover():
    if os.path.exists(FILENAME):
        return pd.read_csv(FILENAME)
    else:
        return pd.DataFrame()

# Overskrive fil og nullstille logg
def reset_logg():
    if os.path.exists(FILENAME):
        os.remove(FILENAME)

st.title("Logging av fuktprøver")

if st.button("Nullstill loggfil (slett alle prøver)"):
    reset_logg()
    st.success("Loggfil nullstilt!")

# Inputfelt
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
onsket_fukt = st.number_input("Ønsket fukt (%)", min_value=0.0, format="%.2f", value=1.36)
beregnet_fukt = st.number_input("Beregnet fukt (%)", min_value=0.0, format="%.2f", value=1.25)
brennkammer_temp = st.number_input("Brennkammertemp (°C)", value=790)
innlop_temp = st.number_input("Innløpstemperatur (°C)", value=400)
utlop_temp = st.number_input("Utløpstemperatur (°C)", value=135)
friskluft = st.number_input("Friskluft (%)", value=12)
primluft = st.number_input("Primærluft (%)", value=3)
trykk_ovn = st.number_input("Trykk ovn (Pa)", value=-270)
hombak = st.number_input("Utmating Hombak (%)", value=78)
maier = st.number_input("Utmating Maier (%)", value=25)

if st.button("Loggfør prøve"):
    ny_prove = {
        "timestamp": timestamp,
        "onsket_fukt": onsket_fukt,
        "beregnet_fukt": beregnet_fukt,
        "brennkammer_temp": brennkammer_temp,
        "innlop_temp": innlop_temp,
        "utlop_temp": utlop_temp,
        "friskluft": friskluft,
        "primluft": primluft,
        "trykk_ovn": trykk_ovn,
        "hombak": hombak,
        "maier": maier
    }
    df = lagre_prove(ny_prove)
    st.success("Prøve logget!")

else:
    df = les_prover()

if not df.empty:
    st.subheader("Oversikt over loggede prøver")
    st.dataframe(df)
else:
    st.info("Ingen prøver logget enda.")

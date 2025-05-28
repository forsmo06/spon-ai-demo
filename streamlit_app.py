import streamlit as st
import pandas as pd
import os

# Filnavn for loggen
LOGG_FIL = "fuktlogg.csv"

# Funksjon for å legge til data i CSV
def logg_prøve(data: dict):
    # Les eksisterende data eller lag ny DataFrame
    if os.path.exists(LOGG_FIL):
        df = pd.read_csv(LOGG_FIL)
    else:
        df = pd.DataFrame()

    # Legg til ny rad
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)

    # Lagre tilbake til CSV
    df.to_csv(LOGG_FIL, index=False)

# Start appen
st.title("Fuktstyring - Loggføring")

# Les inn eksisterende data for å vise antall prøver
if os.path.exists(LOGG_FIL):
    df_logg = pd.read_csv(LOGG_FIL)
    antall_prøver = len(df_logg)
else:
    antall_prøver = 0

st.write(f"Antall prøver lagret: {antall_prøver}")

# Inputfelter - juster etter dine kolonner
ønsket_fukt = st.number_input("Ønsket fukt (%)", min_value=0.0, max_value=100.0, value=1.36, step=0.01)
brennkammertemp = st.slider("Brennkammertemp (°C)", min_value=600, max_value=1000, value=794)
innløpstemp = st.number_input("Innløpstemperatur (°C)", min_value=0, max_value=1000, value=403)
utløpstemp = st.number_input("Utløpstemperatur (°C)", min_value=0, max_value=1000, value=133)
friskluft = st.number_input("Friskluft (%)", min_value=0, max_value=100, value=12)
primluft = st.number_input("Primærluft (%)", min_value=0, max_value=100, value=3)
trykkovn = st.number_input("Trykk ovn (Pa)", min_value=-500, max_value=0, value=-270)
hombak = st.number_input("Utmatning Hombak (%)", min_value=0, max_value=100, value=78)
maier = st.number_input("Utmatning Maier (%)", min_value=0, max_value=100, value=25)

# Knapp for å lagre prøve
if st.button("Loggfør denne prøven"):
    ny_prøve = {
        "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ønsket_fukt": ønsket_fukt,
        "brennkammertemp": brennkammertemp,
        "innløpstemp": innløpstemp,
        "utløpstemp": utløpstemp,
        "friskluft": friskluft,
        "primluft": primluft,
        "trykkovn": trykkovn,
        "hombak": hombak,
        "maier": maier
    }

    logg_prøve(ny_prøve)

    st.success("Prøve lagret!")

    # Oppdater antall prøver i appen
    antall_prøver += 1
    st.write(f"Antall prøver lagret: {antall_prøver}")

import streamlit as st
import pandas as pd
import os
from datetime import datetime
from sklearn.linear_model import LinearRegression

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

def last_inn_data():
    if os.path.exists(FILENAME):
        df = pd.read_csv(FILENAME)
        return df
    else:
        return pd.DataFrame()

def tren_model(df):
    st.write("Kolonner i data:", list(df.columns))

    map_kolonner = {
        "brennkammer_temp": "brennkammer_temp",
        "brennkammertemp": "brennkammer_temp",
        "innlop_temp": "innlop_temp",
        "innløpstemp": "innlop_temp",
        "utlop_temp": "utlop_temp",
        "utløpstemp": "utlop_temp",
        "friskluft": "friskluft",
        "primluft": "primluft",
        "trykk_ovn": "trykk_ovn",
        "trykkovn": "trykk_ovn",
        "hombak": "hombak",
        "maier": "maier"
    }

    nødvendige_kolonner = []
    for k in map_kolonner.keys():
        if k in df.columns:
            nødvendige_kolonner.append(k)

    if not nødvendige_kolonner:
        st.error("Ingen gyldige kolonner for trening funnet i data.")
        return None

    X = df[nødvendige_kolonner].copy()
    X.rename(columns=map_kolonner, inplace=True)

    if "beregnet_fukt" not in df.columns:
        st.error("Data mangler kolonnen 'beregnet_fukt'. Kan ikke trene modellen.")
        return None

    y = df["beregnet_fukt"]

    mask = X.notnull().all(axis=1) & y.notnull()
    X = X.loc[mask]
    y = y.loc[mask]

    if len(X) == 0:
        st.error("Ingen gyldige data igjen etter fjerning av manglende verdier.")
        return None

    model = LinearRegression()
    model.fit(X, y)
    return model

def main():
    st.title("Logging og beregning av fuktprøver")

    # Inputfelter for prøvedata
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    onsket_fukt = st.number_input("Ønsket fukt (%)", min_value=0.0, format="%.2f", value=1.36)
    beregnet_fukt = st.number_input("Beregnet fukt (%)", min_value=0.0, format="%.2f", value=1.25)
    brennkammer_temp = st.number_input("Brennkammertemp (°C)", value=790)
    innlop_temp = st.number_input("Innløpstemp (°C)", value=400)
    utlop_temp = st.number_input("Utløpstemp (°C)", value=135)
    friskluft = st.number_input("Friskluft (%)", value=12)
    primluft = st.number_input("Primærluft (%)", value=3)
    trykk_ovn = st.number_input("Trykk ovn (Pa)", value=-270)
    hombak = st.number_input("Utmating Hombak (%)", value=78)
    maier = st.number_input("Utmating Maier (%)", value=25)

    if st.button("Loggfør prøve"):
        prøve = {
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
        antall = lagre_prove(prøve)
        st.success(f"Prøve loggført! Totalt lagret: {antall}")

    # Vis lagrede prøver
    df = last_inn_data()
    if not df.empty:
        st.header("Oversikt over lagrede prøver")
        st.dataframe(df)

        # Tren modell og vis status
        model = tren_model(df)
        if model:
            st.success("AI-modellen er trent og klar!")
        else:
            st.warning("AI-modellen er ikke klar for trening.")

        # Nullstill logg-knapp
        if st.button("Nullstill logg (slett alle prøver)"):
            os.remove(FILENAME)
            st.experimental_rerun()
    else:
        st.info("Ingen prøver loggført enda.")

if __name__ == "__main__":
    main()

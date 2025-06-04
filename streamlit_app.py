# app.py

import streamlit as st
import pandas as pd
import numpy as np
import os
import datetime
import re

from PIL import Image
import pytesseract

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

# -----------------------------------------------
# Konfigurasjon
# -----------------------------------------------

# Filbane for CSV-logging
DATA_FILE = "data.csv"

# Minimum antall prøver før AI-trening
MIN_SAMPLES = 10

# Målverdier og akseptable intervaller (eksempelverdier, juster etter behov)
TARGET_OUTLET_TEMP = 80.0   # °C
OUTLET_TEMP_TOL = 5.0       # ± toleranse i °C

TARGET_PRESSURE = 1.2       # bar
PRESSURE_TOL = 0.2          # ± toleranse i bar

# Funksjon: Laster eller oppretter CSV for logging
@st.cache_data
def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE, parse_dates=["timestamp"])
    else:
        # Opprett tom DataFrame med kolonner
        columns = [
            "timestamp",
            "brennkammertemp",
            "inlet_temp",
            "outlet_temp",
            "primary_air",
            "pressure",
            "hombak",
            "maier",
            "measured_moisture",
        ]
        df = pd.DataFrame(columns=columns)
        df.to_csv(DATA_FILE, index=False)
    return df

# Funksjon: Lagrer en ny prøve til CSV
def append_sample(row: dict):
    df = load_data()
    df = df.append(row, ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

# Funksjon: Trener AI-modell hvis nok data
@st.cache_data(show_spinner=False)
def train_model(df: pd.DataFrame):
    # Bruk bare prøver som har målt fuktighet
    df_clean = df.dropna(subset=["measured_moisture"])
    if len(df_clean) < MIN_SAMPLES:
        return None

    # Funksjoner og mål
    X = df_clean[
        [
            "brennkammertemp",
            "inlet_temp",
            "outlet_temp",
            "primary_air",
            "pressure",
            "hombak",
            "maier",
        ]
    ]
    y = df_clean["measured_moisture"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    return model

# Funksjon: Enkel parsing av tall fra OCR-tekst
def parse_numbers_from_text(text: str):
    """
    Henter ut alle tall (heltall eller desimal) fra tekst og returnerer som liste av floats.
    """
    matches = re.findall(r"\d+\.?\d*", text)
    numbers = [float(m) for m in matches]
    return numbers

# -----------------------------------------------
# Hovedapplikasjon
# -----------------------------------------------

st.set_page_config(
    page_title="AI-drevet tørkeapp for sponplateproduksjon",
    layout="centered",
    initial_sidebar_state="auto",
)

st.title("🌲 AI-drevet tørkeapp for sponplateproduksjon")

st.markdown("""
Denne applikasjonen hjelper deg med å logge prøver, trene en AI-modell for å forutsi fuktighet, og gi sanntidsfeedback basert på innstillinger og målverdier.
""")

# Last inn tidligere data
df_all = load_data()

# Sidebar: Velg modus
mode = st.sidebar.radio("Velg modus", ("Manuell input", "OCR / Bildeopplasting"))

# Funksjon: Viser feedback-meldinger basert på inngangsverdier
def show_feedback(outlet_temp, pressure):
    # Utløpstemp
    if outlet_temp < TARGET_OUTLET_TEMP - OUTLET_TEMP_TOL:
        st.warning(f"Utløpstemperatur ({outlet_temp:.1f} °C) er under mål ({TARGET_OUTLET_TEMP} ±{OUTLET_TEMP_TOL} °C).")
    elif outlet_temp > TARGET_OUTLET_TEMP + OUTLET_TEMP_TOL:
        st.warning(f"Utløpstemperatur ({outlet_temp:.1f} °C) er over mål ({TARGET_OUTLET_TEMP} ±{OUTLET_TEMP_TOL} °C).")
    else:
        st.success(f"Utløpstemperatur ({outlet_temp:.1f} °C) er innenfor målområdet.")

    # Trykk
    if pressure < TARGET_PRESSURE - PRESSURE_TOL:
        st.warning(f"Trykk ({pressure:.2f} bar) er under mål ({TARGET_PRESSURE} ±{PRESSURE_TOL} bar).")
    elif pressure > TARGET_PRESSURE + PRESSURE_TOL:
        st.warning(f"Trykk ({pressure:.2f} bar) er over mål ({TARGET_PRESSURE} ±{PRESSURE_TOL} bar).")
    else:
        st.success(f"Trykk ({pressure:.2f} bar) er innenfor målområdet.")

# Felter for manuell input
if mode == "Manuell input":
    st.header("🔧 Manuell input av parametere")

    with st.form("manual_form"):
        brennkammer_temp = st.number_input("Brennkammertemperatur (°C)", min_value=0.0, max_value=500.0, step=0.1)
        inlet_temp = st.number_input("Innløpstemperatur (°C)", min_value=0.0, max_value=500.0, step=0.1)
        outlet_temp = st.number_input("Utløpstemperatur (°C)", min_value=0.0, max_value=500.0, step=0.1)
        primary_air = st.number_input("Primærluft (m³/h)", min_value=0.0, max_value=10000.0, step=1.0)
        pressure = st.number_input("Trykk (bar)", min_value=0.0, max_value=10.0, step=0.01)
        hombak = st.number_input("Hombak (kg/h)", min_value=0.0, max_value=10000.0, step=1.0)
        maier = st.number_input("Maier (kg/h)", min_value=0.0, max_value=10000.0, step=1.0)

        st.markdown("**Målt fuktighet (%)**")
        measured_moisture = st.number_input("Målt fuktighet (%)", min_value=0.0, max_value=100.0, step=0.1)

        submitted = st.form_submit_button("Logg prøve")

    if submitted:
        # Lag en rad for logging
        new_row = {
            "timestamp": datetime.datetime.now(),
            "brennkammertemp": brennkammer_temp,
            "inlet_temp": inlet_temp,
            "outlet_temp": outlet_temp,
            "primary_air": primary_air,
            "pressure": pressure,
            "hombak": hombak,
            "maier": maier,
            "measured_moisture": measured_moisture,
        }
        append_sample(new_row)
        st.success("Prøve logget til data.csv")

        # Vis feedback-meldinger
        show_feedback(outlet_temp, pressure)

# OCR / bildeopplasting
else:
    st.header("📷 OCR / Bildeopplasting")
    st.markdown("Last opp et bilde av loggskjema (f.eks. foto av papirark). Appen forsøker å lese av tallene automatisk og fylle inn feltene.")

    uploaded_file = st.file_uploader("Velg bilde (JPG, PNG)", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        try:
            image = Image.open(uploaded_file)
            st.image(image, caption="Lastet opp bilde", use_column_width=True)

            # Utfør OCR
            text = pytesseract.image_to_string(image, lang="nor+eng")
            st.text_area("OCR-utskrift (råtekst)", text, height=200)

            # Pars tall
            nums = parse_numbers_from_text(text)
            st.write(f"Fant disse tallverdiene (i rekkefølge): {nums}")

            # Forutsetter en ordning: [brennkammer, inlet, outlet, primær luft, trykk, hombak, maier, målt fukt]
            if len(nums) >= 8:
                brennkammer_temp = nums[0]
                inlet_temp = nums[1]
                outlet_temp = nums[2]
                primary_air = nums[3]
                pressure = nums[4]
                hombak = nums[5]
                maier = nums[6]
                measured_moisture = nums[7]
                st.success("Verdier fylt inn automatisk fra bilde.")
            else:
                st.error("Kunne ikke finne nok tall i bildet for automatisk utfylling. Vennligst fyll inn manuelt under.")

                brennkammer_temp = st.number_input("Brennkammertemperatur (°C)", min_value=0.0, max_value=500.0, step=0.1)
                inlet_temp = st.number_input("Innløpstemperatur (°C)", min_value=0.0, max_value=500.0, step=0.1)
                outlet_temp = st.number_input("Utløpstemperatur (°C)", min_value=0.0, max_value=500.0, step=0.1)
                primary_air = st.number_input("Primærluft (m³/h)", min_value=0.0, max_value=10000.0, step=1.0)
                pressure = st.number_input("Trykk (bar)", min_value=0.0, max_value=10.0, step=0.01)
                hombak = st.number_input("Hombak (kg/h)", min_value=0.0, max_value=10000.0, step=1.0)
                maier = st.number_input("Maier (kg/h)", min_value=0.0, max_value=10000.0, step=1.0)
                measured_moisture = st.number_input("Målt fuktighet (%)", min_value=0.0, max_value=100.0, step=0.1)

            if st.button("Logg prøve fra OCR"):
                # Logg prøve
                new_row = {
                    "timestamp": datetime.datetime.now(),
                    "brennkammertemp": brennkammer_temp,
                    "inlet_temp": inlet_temp,
                    "outlet_temp": outlet_temp,
                    "primary_air": primary_air,
                    "pressure": pressure,
                    "hombak": hombak,
                    "maier": maier,
                    "measured_moisture": measured_moisture,
                }
                append_sample(new_row)
                st.success("Prøve logget til data.csv")

                # Vis feedback-meldinger
                show_feedback(outlet_temp, pressure)

        except Exception as e:
            st.error(f"Kunne ikke lese bildet: {e}")

# -----------------------------------------------
# Vis AI-prediksjon og historikk
# -----------------------------------------------

st.markdown("---")
st.header("🤖 AI-prediksjon og historikk")

df_all = load_data()

# Vis antall prøver
st.write(f"Totalt antall registrerte prøver: {len(df_all)}")

# Sjekk om vi kan trene modell
model = train_model(df_all)

if model is None:
    st.info(f"Vent på minst {MIN_SAMPLES} prøver før AI-trening (har nå {len(df_all)}).")
else:
    st.success("AI-modell trent! Velg parametere nedenfor for sanntidsprediksjon.")

    with st.form("predict_form"):
        pred_brennkammer_temp = st.number_input("Brennkammertemperatur (°C)", min_value=0.0, max_value=500.0, step=0.1, key="pred1")
        pred_inlet_temp = st.number_input("Innløpstemperatur (°C)", min_value=0.0, max_value=500.0, step=0.1, key="pred2")
        pred_outlet_temp = st.number_input("Utløpstemperatur (°C)", min_value=0.0, max_value=500.0, step=0.1, key="pred3")
        pred_primary_air = st.number_input("Primærluft (m³/h)", min_value=0.0, max_value=10000.0, step=1.0, key="pred4")
        pred_pressure = st.number_input("Trykk (bar)", min_value=0.0, max_value=10.0, step=0.01, key="pred5")
        pred_hombak = st.number_input("Hombak (kg/h)", min_value=0.0, max_value=10000.0, step=1.0, key="pred6")
        pred_maier = st.number_input("Maier (kg/h)", min_value=0.0, max_value=10000.0, step=1.0, key="pred7")

        predict_clicked = st.form_submit_button("Beregn forventet fuktighet")

    if predict_clicked:
        X_pred = np.array(
            [
                pred_brennkammer_temp,
                pred_inlet_temp,
                pred_outlet_temp,
                pred_primary_air,
                pred_pressure,
                pred_hombak,
                pred_maier,
            ]
        ).reshape(1, -1)
        pred_moisture = model.predict(X_pred)[0]
        st.metric("Forventet fuktighet (%)", f"{pred_moisture:.2f}")

# Vis de siste 10 prøvene
st.markdown("### 📈 Siste 10 prøver")
if not df_all.empty:
    st.dataframe(df_all.sort_values(by="timestamp", ascending=False).head(10))
else:
    st.write("Ingen data å vise ennå.")

# -----------------------------------------------
# Slutt
# -----------------------------------------------

st.markdown("""
---
*Denne appen kjører på Streamlit. For å starte kjøring lokalt:*

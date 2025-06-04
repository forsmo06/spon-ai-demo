import streamlit as st
import pandas as pd
import os
from datetime import datetime
from sklearn.linear_model import LinearRegression
import joblib

# === Konfigurasjon ===
st.set_page_config(layout="wide")
st.title("📊 Fuktstyring – AI & Manuell (Ipar-stil)")

LOGG_FIL = "fuktlogg.csv"
MODELL_FIL = "fuktmodell.pkl"

# === Status i sidepanelet ===
if os.path.exists(LOGG_FIL):
    df_log = pd.read_csv(LOGG_FIL)
    antall = len(df_log)
    if antall < 10:
        st.sidebar.info(f"📊 {antall} av 10 prøver – AI inaktiv")
    else:
        st.sidebar.success(f"🤖 AI aktiv (basert på {antall} prøver)")
else:
    st.sidebar.info("📊 Ingen prøver logget – AI inaktiv")

# === Oppsett: To kolonner med ulik bredde ===
col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("🔧 Innstillinger sponavd")

    target_fukt = st.number_input(
        "Ønsket fukt (%)",
        min_value=0.5, max_value=4.0, step=0.01, value=1.36,
        help="Mål for fuktighet i ferdig plate"
    )

    st.markdown("**Primære parametere**")
    brennkammer = st.slider(
        "Brennkammertemp (°C)", 600, 1000, 794,
        help="Temperatur inne i brennkammeret"
    )
    temp_til = st.slider(
        "Innløpstemp (G80GT105) (°C)", 250, 700, 403,
        help="Temperatur inn i tørketrommel"
    )
    temp_ut = st.slider(
        "Utløpstemp (G80GT106) (°C)", 100, 180, 133,
        help="Temperatur ut av tørketrommel (for 22 mm plate: 133–137 °C)"
    )

    with st.expander("Avanserte parametere"):
        friskluft = st.slider(
            "Forbrenning av støv – Friskluft (GS5P101) (%)", 0, 100, 12,
            help="Mengde friskluft til forbrenning av støv"
        )
        primluft = st.slider(
            "Primærluftsflekt (GS5F101) (%)", 0, 100, 3,
            help="Hovedluft til ovn"
        )
        trykkovn = st.slider(
            "Trykk ovn (G80GP101) (Pa)", -500, 0, -270,
            help="Negativt trykk i ovnsrommet"
        )
        hombak = st.slider(
            "Utmating Hombak (%)", 0, 100, 78,
            help="Mengde tørrspon som mates ut fra Hombak"
        )
        maier = st.slider(
            "Utmating Maier (%)", 0, 100, 25,
            help="Spon fra Maier-møllen"
        )

    st.markdown("---")
    if st.button("📥 Lagre måling"):
        # Lag input-ordbok for loggføring
        input_data = {
            "brennkammertemp": brennkammer,
            "innløpstemp": temp_til,
            "utløpstemp": temp_ut,
            "friskluft": friskluft,
            "primluft": primluft,
            "trykkovn": trykkovn,
            "hombak": hombak,
            "maier": maier,
            "ønsket_fukt": target_fukt,
            "timestamp": datetime.now().isoformat()
        }
        # Les eksisterende, legg til ny rad, skriv tilbake
        if os.path.exists(LOGG_FIL):
            df_existing = pd.read_csv(LOGG_FIL)
            df_combined = pd.concat([df_existing, pd.DataFrame([input_data])], ignore_index=True)
        else:
            df_combined = pd.DataFrame([input_data])
        df_combined.to_csv(LOGG_FIL, index=False)
        st.success("✅ Måling lagret i fuktlogg.csv")

with col2:
    st.subheader("📈 Resultat")

    # === Hjelpefunksjoner for AI-modellen ===
    def hent_modell():
        if os.path.exists(MODELL_FIL):
            try:
                return joblib.load(MODELL_FIL)
            except:
                return None
        return None

    def tren_modell():
        df = pd.read_csv(LOGG_FIL)
        if len(df) < 10:
            return None
        X = df[[
            "brennkammertemp", "innløpstemp", "utløpstemp",
            "friskluft", "primluft", "trykkovn", "hombak", "maier"
        ]]
        y = df["ønsket_fukt"]
        m = LinearRegression().fit(X, y)
        joblib.dump(m, MODELL_FIL)
        return m

    def beregn_ai(data):
        modell = hent_modell()
        if modell is None and os.path.exists(LOGG_FIL):
            df = pd.read_csv(LOGG_FIL)
            if len(df) >= 10:
                modell = tren_modell()
        if modell is None:
            return None
        return round(modell.predict(pd.DataFrame([data]))[0], 2)

    # === Bygg input-ordbok til prediksjon ===
    input_data = {
        "brennkammertemp": brennkammer,
        "innløpstemp": temp_til,
        "utløpstemp": temp_ut,
        "friskluft": friskluft,
        "primluft": primluft,
        "trykkovn": trykkovn,
        "hombak": hombak,
        "maier": maier
    }

    ai_fukt = beregn_ai(input_data)
    fukt = ai_fukt if ai_fukt is not None else 1.00
    diff = round(fukt - target_fukt, 2)

    st.metric("🔹 Beregnet fukt", f"{fukt:.2f} %", delta_color="off")
    st.metric("🎯 Ønsket fukt", f"{target_fukt:.2f} %", delta_color="off")
    st.metric("➖ Avvik", f"{diff:+.2f} %", delta_color="normal")

    # --- Enkle advarsler / bekreftelser ---
    if temp_ut < 133 or temp_ut > 137:
        st.warning("⚠️ Utløpstemp utenfor mål (133–137 °C)")
    else:
        st.success("✅ Utløpstemp OK")

    if trykkovn != -270:
        st.warning("ℹ️ Trykk ovn avviker fra -270 Pa")
    else:
        st.success("✅ Trykk ovn OK")

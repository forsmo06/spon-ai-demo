import streamlit as st
import numpy as np
import pandas as pd
import os
from datetime import datetime
from sklearn.linear_model import LinearRegression

# === Konfigurasjon ===
st.set_page_config(layout="wide")
st.title("📊 Fuktstyring – AI & Manuell (Ipaar-stil)")

LOGG_FIL = "fuktlogg.csv"
MODELL_FIL = "fuktmodell.pkl"

# === Funksjon for logging av prøver ===
def logg_data(data):
    df = pd.DataFrame([data])
    if os.path.exists(LOGG_FIL):
        df_existing = pd.read_csv(LOGG_FIL)
        df = pd.concat([df_existing, df], ignore_index=True)
    df.to_csv(LOGG_FIL, index=False)

# === Vis status for antall prøver ===
if os.path.exists(LOGG_FIL):
    df_log = pd.read_csv(LOGG_FIL)
    antall = len(df_log)
    if antall < 10:
        st.sidebar.info(f"📊 Antall prøver: {antall} av 10 – AI ikke aktiv ennå")
    else:
        st.sidebar.success(f"🤖 AI aktiv ✅ – basert på {antall} prøver")
else:
    st.sidebar.info("📊 Ingen prøver funnet enda – AI ikke aktiv")

# === VINSTRE SIDE: INNSTILLINGER (manuell inntasting) ===
col1, col2 = st.columns(2)
with col1:
    st.header("🔧 Sponavd Manuell")

    target_fukt = st.number_input(
        "Ønsket fukt (%)", 
        min_value=0.5, max_value=4.0, step=0.01, value=1.36
    )

    brennkammer = st.slider(
        "Brennkammertemp (°C)", 600, 1000, value=794
    )
    temp_til = st.slider(
        "Innløpstemp (G80GT105) (°C)", 250, 700, value=403
    )
    temp_ut = st.slider(
        "Utløpstemp (G80GT106) (°C)", 100, 180, value=133
    )
    friskluft = st.slider(
        "Forbrenning av støv – Friskluft (GS5P101) (%)", 0, 100, value=12
    )
    primluft = st.slider(
        "Primærluftsflekt (GS5F101) (%)", 0, 100, value=3
    )
    trykkovn = st.slider(
        "Trykk ovn (G80GP101) (Pa)", -500, 0, value=-270
    )
    hombak = st.slider(
        "Utmating Hombak (%)", 0, 100, value=78
    )
    maier = st.slider(
        "Utmating Maier (%)", 0, 100, value=25
    )

# === AI-BEREGNING ===
def hent_trent_model():
    from sklearn.externals import joblib
    # joblib finnes ikke i nyeste sklearn, men om du har installert separat
    # kan du endre til: import joblib
    if os.path.exists(MODELL_FIL):
        try:
            import joblib
            return joblib.load(MODELL_FIL)
        except:
            return None
    return None

def tren_og_lagre_model():
    import joblib
    df = pd.read_csv(LOGG_FIL)
    if len(df) < 10:
        return None
    X = df[[
        "brennkammertemp", "innløpstemp", "utløpstemp",
        "friskluft", "primluft", "trykkovn", "hombak", "maier"
    ]]
    y = df["ønsket_fukt"]
    model = LinearRegression().fit(X, y)
    joblib.dump(model, MODELL_FIL)
    return model

def beregn_med_ai(data):
    # Hent modell om den finnes, ellers tren hvis nok data
    model = hent_trent_model()
    if model is None:
        if os.path.exists(LOGG_FIL):
            df_log = pd.read_csv(LOGG_FIL)
            if len(df_log) >= 10:
                model = tren_og_lagre_model()
    if model is None:
        return None
    data_df = pd.DataFrame([data])
    return round(model.predict(data_df)[0], 2)

# === HØYRE SIDE: RESULTAT ===
with col2:
    st.header("📈 Resultat")

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

    ai_fukt = beregn_med_ai(input_data)
    fukt = ai_fukt if ai_fukt is not None else 1.0  # fallback
    diff = round(fukt - target_fukt, 2)

    st.metric("🔹 Beregnet fukt", f"{fukt:.2f} %")
    st.metric("🎯 Ønsket fukt", f"{target_fukt:.2f} %")
    st.metric("➖ Avvik", f"{diff:+.2f} %")

    # Enkle advarsler for temperatur og trykk
    if temp_ut > 137 or temp_ut < 133:
        st.warning("⚠️ Utløpstemp utenfor mål for 22mm gulvplate (133–137 °C)")
    else:
        st.success("✅ Utløpstemp OK for 22mm gulvplate")

    if trykkovn != -270:
        st.warning("ℹ️ Trykk ovn avviker fra anbefalt -270 Pa")
    else:
        st.success("✅ Trykk ovn OK")

    # Loggfør knapp
    if st.button("📥 Loggfør denne prøven"):
        logg_data({
            "timestamp": datetime.now().isoformat(),
            "ønsket_fukt": target_fukt,
            "beregnet_fukt": fukt,
            **input_data
        })
        st.success("✅ Prøve lagret til fuktlogg.csv")
        if ai_fukt is None:
            st.info("ℹ️ Når minst 10 prøver er lagret, vil AI begynne å lære og brukes i beregningene.")

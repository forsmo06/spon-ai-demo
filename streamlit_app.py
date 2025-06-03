import streamlit as st
import numpy as np
import pandas as pd
import os
from datetime import datetime
from sklearn.linear_model import LinearRegression
from PIL import Image
import pytesseract

st.set_page_config(layout="wide")

st.title("📊 Fuktstyring – AI & Manuell (Ipaar-stil)")

col1, col2 = st.columns(2)

# === Funksjon for logging av prøver ===
LOGG_FIL = "fuktlogg.csv"

def logg_data(data):
    df = pd.DataFrame([data])
    if os.path.exists(LOGG_FIL):
        df_existing = pd.read_csv(LOGG_FIL)
        df = pd.concat([df_existing, df], ignore_index=True)
    df.to_csv(LOGG_FIL, index=False)

# === Vis status for antall prøver uansett ===
if os.path.exists(LOGG_FIL):
    df = pd.read_csv(LOGG_FIL)
    antall = len(df)
    if antall < 10:
        st.sidebar.info(f"📊 Antall prøver: {antall} av 10 – AI ikke aktiv ennå")
    else:
        st.sidebar.success(f"🤖 AI aktiv ✅ – basert på {antall} prøver")

# === Bildeopplasting og OCR-forslag ===
st.sidebar.header("📸 Last opp bilde av måling")
lastet_bilde = st.sidebar.file_uploader("Dra inn et bilde av logg (PNG/JPG)", type=["png", "jpg", "jpeg"])
ocr_data = {}

if lastet_bilde:
    bilde = Image.open(lastet_bilde)
    tekst = pytesseract.image_to_string(bilde)
    st.sidebar.text_area("📄 Gjenkjent tekst", tekst)

    import re
    tall = re.findall(r"[-+]?[0-9]*\.?[0-9]+", tekst)
    if len(tall) >= 8:
        try:
            ocr_data = {
                "brennkammertemp": int(float(tall[0])),
                "innløpstemp": int(float(tall[1])),
                "utløpstemp": int(float(tall[2])),
                "friskluft": int(float(tall[3])),
                "primluft": int(float(tall[4])),
                "trykkovn": int(float(tall[5])),
                "hombak": int(float(tall[6])),
                "maier": int(float(tall[7])),
            }
            st.sidebar.success("✅ Forslag hentet fra bilde")
        except:
            st.sidebar.warning("⚠️ Klarte ikke tolke alle tall fra bildet")

# === VENSTRE SIDE: INNSTILLINGER ===
with col1:
    st.header("🔧 Sponavd AI-styrt")

    target_fukt = st.number_input("Ønsket fukt (%)", 0.5, 4.0, step=0.01, value=1.36)

    brennkammer = st.number_input("Brennkammertemp (°C)", 600, 1000, step=1, value=ocr_data.get("brennkammertemp", 794))
    temp_til = st.number_input("Innløpstemp (°C)", 250, 700, step=1, value=ocr_data.get("innløpstemp", 403))
    temp_ut = st.number_input("Utløpstemp (°C)", 100, 180, step=1, value=ocr_data.get("utløpstemp", 133))
    friskluft = st.number_input("Forbrenning av støv – Friskluft (%)", 0, 100, step=1, value=ocr_data.get("friskluft", 12))
    primluft = st.number_input("Primærluft (%)", 0, 100, step=1, value=ocr_data.get("primluft", 3))
    trykkovn = st.number_input("Trykk ovn (Pa)", -500, 0, step=1, value=ocr_data.get("trykkovn", -270))
    hombak = st.number_input("Utmating Hombak (%)", 0, 100, step=1, value=ocr_data.get("hombak", 78))
    maier = st.number_input("Utmating Maier (%)", 0, 100, step=1, value=ocr_data.get("maier", 25))

# === AI-BEREGNING ===
def beregn_med_ai(data):
    if not os.path.exists(LOGG_FIL):
        return None
    df = pd.read_csv(LOGG_FIL)
    if len(df) < 10:
        return None
    X = df[["brennkammertemp", "innløpstemp", "utløpstemp", "friskluft", "primluft", "trykkovn", "hombak", "maier"]]
    y = df["ønsket_fukt"]
    model = LinearRegression().fit(X, y)
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
    fukt = ai_fukt if ai_fukt is not None else 1.0
    diff = round(fukt - target_fukt, 2)

    st.metric("🔹 Beregnet fukt", f"{fukt:.2f} %")
    st.metric("🎯 Ønsket fukt", f"{target_fukt:.2f} %")
    st.metric("➖ Avvik", f"{diff:+.2f} %")

    if temp_ut > 137 or temp_ut < 133:
        st.warning("⚠️ Utløpstemp utenfor mål for 22mm gulvplate (133–137 °C)")
    else:
        st.success("✅ Utløpstemp OK")

    if trykkovn != -270:
        st.warning("ℹ️ Trykk ovn avviker fra anbefalt -270 Pa")
    else:
        st.success("✅ Trykk ovn OK")

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

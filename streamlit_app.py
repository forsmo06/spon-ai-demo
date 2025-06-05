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

# === Logging av data ===
def logg_data(data):
    df = pd.DataFrame([data])
    if os.path.exists(LOGG_FIL):
        df_existing = pd.read_csv(LOGG_FIL)
        df = pd.concat([df_existing, df], ignore_index=True)
    df.to_csv(LOGG_FIL, index=False)

# === AI-beregning ===
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

# === Layout ===
col1, col2 = st.columns(2)

with col1:
    st.header("🔧 Sponavd AI-styrt")

    target_fukt = st.number_input("Ønsket fukt (%)", 0.5, 4.0, step=0.01, value=1.36)

    brennkammer = st.slider("Brennkammertemp (°C)", 600, 1000, 794)
    temp_til = st.slider("Innløpstemp (°C)", 250, 700, 403)
    temp_ut = st.slider("Utløpstemp (°C)", 100, 180, 133)
    friskluft = st.slider("Friskluft (%)", 0, 100, 12)
    primluft = st.slider("Primærluft (%)", 0, 100, 3)
    trykkovn = st.slider("Trykk ovn (Pa)", -500, 0, -270)
    hombak = st.slider("Utmating Hombak (%)", 0, 100, 78)
    maier = st.slider("Utmating Maier (%)", 0, 100, 25)

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
        st.success("✅ Utløpstemp OK for 22mm gulvplate")

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
        st.success("✅ Prøve lagret")

# === Vis historiske logger ===
st.subheader("📚 Loggede prøver")
if os.path.exists(LOGG_FIL):
    df = pd.read_csv(LOGG_FIL)
    st.dataframe(df.tail(10), use_container_width=True)
else:
    st.info("Ingen prøver logget ennå.")

# === Enkel AI-chat i hjørnet ===
with st.expander("💬 Trenger du hjelp? Klikk her for å spørre!"):
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    def hent_svar_fra_manual(sporsmal):
        s = sporsmal.lower()
        if "utløpstemp" in s:
            return "Utløpstemp er temperaturen etter tørka. Den påvirker fuktigheten i spona."
        elif "loggføre" in s:
            return "For å loggføre en prøve, still inn verdiene og trykk på 'Loggfør denne prøven'-knappen."
        elif "fukt for lav" in s or "fukta for lav" in s:
            return "Hvis fukta er for lav, kan du senke utløpstemp eller redusere friskluft/innmating."
        elif "starte tørka" in s:
            return "Sjekk at systemet er i auto, og at alle verdier er innenfor grenser før du starter."
        elif "hombak" in s:
            return "Hombak er innmatingen for tørr spon. Juster den i prosent etter behov."
        elif "maier" in s:
            return "Maier er innmatingen for fuktig sagflis. Brukes mer ved lav innløpstemp."
        elif "trykk" in s:
            return "Trykk i ovnen skal ligge rundt -270 Pa. Går det mye utenfor, si ifra."
        else:
            return "Beklager, jeg forsto ikke spørsmålet helt. Prøv å stille det på en litt annen måte."

    user_input = st.text_input("Skriv spørsmålet ditt her")
    if user_input:
        svar = hent_svar_fra_manual(user_input)
        st.session_state.chat_history.append(("👤 Du", user_input))
        st.session_state.chat_history.append(("🤖 Hjelperen", svar))

    for rolle, melding in st.session_state.chat_history:
        st.write(f"**{rolle}:** {melding}")

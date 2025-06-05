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
    brennkammer = st.slider("Brennkammertemp (°C)", 600, 1000, 794)
    temp_til = st.slider("Innløpstemp (°C)", 250, 700, 403)
    temp_ut = st.slider("Utløpstemp (°C)", 100, 180, 133)

    with st.expander("Avanserte parametere"):
        friskluft = st.slider("Friskluft (%)", 0, 100, 12)
        primluft = st.slider("Primærluft (%)", 0, 100, 3)
        trykkovn = st.slider("Trykk ovn (Pa)", -500, 0, -270)
        hombak = st.slider("Utmating Hombak (%)", 0, 100, 78)
        maier = st.slider("Utmating Maier (%)", 0, 100, 25)

    st.markdown("---")
    if st.button("📥 Lagre måling"):
        input_data = {
            "timestamp": datetime.now().isoformat(),
            "ønsket_fukt": target_fukt,
            "brennkammertemp": brennkammer,
            "innløpstemp": temp_til,
            "utløpstemp": temp_ut,
            "friskluft": friskluft,
            "primluft": primluft,
            "trykkovn": trykkovn,
            "hombak": hombak,
            "maier": maier
        }
        if os.path.exists(LOGG_FIL):
            df_existing = pd.read_csv(LOGG_FIL)
            df_combined = pd.concat([df_existing, pd.DataFrame([input_data])], ignore_index=True)
        else:
            df_combined = pd.DataFrame([input_data])
        df_combined.to_csv(LOGG_FIL, index=False)
        st.success("✅ Måling lagret i fuktlogg.csv")

with col2:
    st.subheader("📈 Resultat")

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
        X = df[["brennkammertemp", "innløpstemp", "utløpstemp", "friskluft", "primluft", "trykkovn", "hombak", "maier"]]
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

    st.metric("🔹 Beregnet fukt", f"{fukt:.2f} %")
    st.metric("🎯 Ønsket fukt", f"{target_fukt:.2f} %")
    st.metric("➖ Avvik", f"{diff:+.2f} %")

    if temp_ut < 133 or temp_ut > 137:
        st.warning("⚠️ Utløpstemp utenfor mål (133–137 °C)")
    else:
        st.success("✅ Utløpstemperatur OK")

    if trykkovn != -270:
        st.warning("ℹ️ Trykk ovn avviker fra -270 Pa")
    else:
        st.success("✅ Trykk ovn OK")

# === Nederst: Vis alle lagrede tester i en Excel-lignende tabell ===
st.markdown("---")
st.subheader("📋 Alle lagrede prøver")

if os.path.exists(LOGG_FIL):
    df_vis = pd.read_csv(LOGG_FIL)
    df_vis["timestamp"] = pd.to_datetime(df_vis["timestamp"])
    st.dataframe(df_vis)
else:
    st.info("Ingen lagrede prøver ennå. Trykk 'Lagre måling' for å begynne å samle data.")

# === Enkel AI-chat i hjørnet ===
with st.expander("💬 Trenger du hjelp? Klikk her for å spørre!"):
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    def hent_svar_fra_manual(sporsmal):
        s = sporsmal.lower()
        if "utløpstemp" in s:
            return "Utløpstemp er temperaturen etter tørka. Den påvirker fuktigheten i spona."
        elif "loggføre" in s:
            return "For å loggføre en prøve, still inn verdiene og trykk på 'Lagre måling'-knappen."
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

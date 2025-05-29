import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Sponavd AI styrt", layout="wide")

st.title("🔧 Sponavd AI styrt")

# Filnavn for lagring
LOGG_FIL = "fuktlogg.csv"

# Funksjoner for lagring og lesing av logg
def loggfør_prøve(data_dict):
    if os.path.exists(LOGG_FIL):
        df_logg = pd.read_csv(LOGG_FIL)
    else:
        df_logg = pd.DataFrame()
    df_logg = pd.concat([df_logg, pd.DataFrame([data_dict])], ignore_index=True)
    df_logg.to_csv(LOGG_FIL, index=False)
    st.success(f"Prøve loggført! Totalt lagret: {len(df_logg)} prøver.")

def les_logg():
    if os.path.exists(LOGG_FIL):
        df_logg = pd.read_csv(LOGG_FIL)
        return df_logg
    else:
        return pd.DataFrame()

# --- Input og justeringer ---
st.header("Justeringer manuelt og via tekst")

def slider_og_input(nøkkel, label, min_val, max_val, steg=1, format_str=None):
    if nøkkel not in st.session_state:
        st.session_state[nøkkel] = min_val
    col1, col2 = st.columns([3,1])
    with col1:
        val = st.slider(label, min_val, max_val, st.session_state[nøkkel], step=steg)
    with col2:
        val_input = st.number_input(label + " (input)", min_val, max_val, st.session_state[nøkkel], step=steg, format=format_str)
    # Synkroniser begge veier
    if val != st.session_state[nøkkel]:
        st.session_state[nøkkel] = val
    if val_input != st.session_state[nøkkel]:
        st.session_state[nøkkel] = val_input
    return st.session_state[nøkkel]

# Ønsket fukt - tekstfelt med desimal (string for å bruke komma)
ønsket_fukt_str = st.text_input("Ønsket fukt (%)", "1,36")
try:
    ønsket_fukt = float(ønsket_fukt_str.replace(",", "."))
except:
    ønsket_fukt = 0.0
    st.error("Ugyldig format på ønsket fukt. Bruk punktum eller komma som desimal.")

brennkammer_temp = slider_og_input("brennkammer_temp", "Brennkammertemp (°C)", 600, 1000, steg=1)
innlop_temp = slider_og_input("innlop_temp", "Innløpstemp (°C)", 250, 700, steg=1)
utlop_temp = slider_og_input("utlop_temp", "Utløpstemp (°C)", 100, 180, steg=1)
primaerluft = slider_og_input("primaerluft", "Primærluft (%)", 0, 100, steg=1)
trykk_ovn = slider_og_input("trykk_ovn", "Trykk ovn (Pa)", -500, 0, steg=1)
utmating_hombak = slider_og_input("utmating_hombak", "Utmating Hombak (%)", 0, 100, steg=1)
utmating_maier = slider_og_input("utmating_maier", "Utmating Maier (%)", 0, 100, steg=1)

# --- Beregning (dummy eksempel) ---
# Bytt ut med din egen AI-modell eller formel
def beregn_fukt(ønsket, brenn, inn, ut, primaer, trykk, hombak, maier):
    # Dummy: tar ønsket fukt minus 0.1 prosent for demo
    return max(0, ønsket - 0.1)

beregnet_fukt = beregn_fukt(ønsket_fukt, brennkammer_temp, innlop_temp, utlop_temp, primaerluft, trykk_ovn, utmating_hombak, utmating_maier)

# --- Vis resultat ---
st.header("📈 Resultat")

col_res1, col_res2, col_res3 = st.columns(3)
col_res1.metric("Beregned fukt", f"{beregnet_fukt:.2f} %")
col_res2.metric("Ønsket fukt", f"{ønsket_fukt:.2f} %")
avvik = ønsket_fukt - beregnet_fukt
col_res3.metric("Avvik", f"{avvik:.2f} %")

# --- Loggføring ---
if st.button("🔥 Loggfør denne prøven"):
    data_prøve = {
        "onsket_fukt": ønsket_fukt,
        "brennkammer_temp": brennkammer_temp,
        "innlop_temp": innlop_temp,
        "utlop_temp": utlop_temp,
        "primaerluft": primaerluft,
        "trykk_ovn": trykk_ovn,
        "utmating_hombak": utmating_hombak,
        "utmating_maier": utmating_maier,
        "beregnet_fukt": beregnet_fukt,
    }
    loggfør_prøve(data_prøve)

# --- Vis logg ---
st.header("Oversikt over lagrede prøver")
df_logg = les_logg()
if df_logg.empty:
    st.write("Ingen prøver loggført ennå.")
else:
    st.dataframe(df_logg)

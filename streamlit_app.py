import streamlit as st
import numpy as np

st.set_page_config(layout="wide")

st.title("📊 Fuktstyring – AI & Manuell (Ipaar-stil)")

col1, col2 = st.columns(2)

# === VENSTRE SIDE: INNSTILLINGER ===
with col1:
    st.header("🔧 Justeringer")

    target_fukt = st.number_input("Ønsket fukt (%)", 0.5, 4.0, step=0.01, value=1.36)

    brennkammer = st.slider("Brennkammertemp (°C)", 600, 1000, 794)
    temp_til = st.slider("G80GT105 – Innløpstemp (°C)", 250, 700, 403)
    temp_ut = st.slider("G80GT106 – Utløpstemp (°C)", 100, 180, 133)
    friskluft = st.slider("GS5P101 – Friskluft (Forbrenning av støv) (%)", 0, 100, 12)
    primluft = st.slider("GS5F101 – Primærluftsflekt (%)", 0, 100, 3)
    trykkovn = st.slider("G80GP101 – Trykk ovn (Pa)", -500, 0, -270)
    hombak = st.slider("Utmating Hombak (%)", 0, 100, 78)
    maier = st.slider("Utmating Maier (%)", 0, 100, 25)

# === HØYRE SIDE: RESULTAT ===
with col2:
    st.header("📈 Resultat")

    def beregn_fukt(brenn, g105, g106, frisk, prim, trykk, hombak, maier):
        # Økt vekt på utløpstemp, redusert innflytelse fra friskluft og primærluft
        return round(
            2.0
            - (g106 - 130) * 0.055  # Utløpstemp har størst påvirkning
            + (frisk - 60) * 0.005
            + (prim - 30) * 0.005
            + ((trykk + 270) / 100) * 0.15
            + (hombak - 50) * 0.012
            + (maier - 50) * 0.01,
            2
        )

    fukt = beregn_fukt(brennkammer, temp_til, temp_ut, friskluft, primluft, trykkovn, hombak, maier)
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

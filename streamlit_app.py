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
    temp_til = st.slider("Innløpstemp (G80GT105) (°C)", 250, 700, 403)
    temp_ut = st.slider("Utløpstemp (G80GT106) (°C)", 100, 180, 133)
    friskluft = st.slider("Forbrenning av støv – Friskluft (GS5P101) (%)", 0, 100, 12)
    primluft = st.slider("Primærluftsflekt (GS5F101) (%)", 0, 100, 3)
    trykkovn = st.slider("Trykk ovn (G80GP101) (Pa)", -500, 0, -270)
    hombak = st.slider("Utmating Hombak (%)", 0, 100, 78)
    maier = st.slider("Utmating Maier (%)", 0, 100, 25)

# === HØYRE SIDE: RESULTAT ===
with col2:
    st.header("📈 Resultat")

    def beregn_fukt(brenn, g105, g106, frisk, prim, trykk, hombak, maier):
        return round(
            0.91
            - (g106 - 134) * 0.55     # Økt vekt på utløpstemp
            + (prim - 7) * 0.002      # Justert vekt primærluft
            + ((trykk + 270) / 100) * 0.03
            + (hombak - 70) * 0.004
            + (maier - 20) * 0.0025,
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

import streamlit as st
import numpy as np
import re

st.set_page_config(layout="wide")

st.title("📊 Fuktstyring – AI & Manuell (Ipaar-stil)")

col1, col2 = st.columns(2)

# === VENSTRE SIDE: INNSTILLINGER ===
with col1:
    st.header("💬 Kommandobasert styring")

    kommando = st.text_input("Skriv kommando (f.eks. 'Still inn til 1.10% fuktighet')")

    # Standardverdier
    ai_target_fukt = 1.20
    ai_temp_til = 400
    ai_temp_ut = 135
    ai_friskluft = 60
    ai_primluft = 30
    ai_trykkovn = -270
    ai_hombak = 50
    ai_maier = 50

    # Enkle regler for parsing
    if "fukt" in kommando.lower():
        match = re.search(r"(\d+[.,]?\d*)\s*%?\s*fukt", kommando)
        if match:
            ai_target_fukt = float(match.group(1).replace(",", "."))

    if "hombak" in kommando.lower():
        match = re.search(r"hombak.*?(\d+)%", kommando)
        if match:
            ai_hombak = int(match.group(1))

    if "maier" in kommando.lower():
        match = re.search(r"maier.*?(\d+)%", kommando)
        if match:
            ai_maier = int(match.group(1))

    if "utløp" in kommando.lower():
        match = re.search(r"utløp.*?(\d+)", kommando)
        if match:
            ai_temp_ut = int(match.group(1))

    if "innløp" in kommando.lower():
        match = re.search(r"innløp.*?(\d+)", kommando)
        if match:
            ai_temp_til = int(match.group(1))

    st.write("✳️ AI-forslag fra kommando:")
    st.write(f"• Ønsket fukt: {ai_target_fukt} %")
    st.write(f"• Innløpstemp: {ai_temp_til} °C")
    st.write(f"• Utløpstemp: {ai_temp_ut} °C")
    st.write(f"• Hombak: {ai_hombak} %, Maier: {ai_maier} %")

    bruk_ai = st.checkbox("⚙️ Bruk AI-forslag i innstillingene", value=False)

    st.header("🔧 Justeringer")

    target_fukt = st.number_input("Ønsket fukt (%)", 0.5, 4.0, step=0.01, value=ai_target_fukt if bruk_ai else 1.20)
    temp_til = st.slider("G80GT105 – Innløpstemp (°C)", 250, 700, ai_temp_til if bruk_ai else 400)
    temp_ut = st.slider("G80GT106 – Utløpstemp (°C)", 100, 180, ai_temp_ut if bruk_ai else 135)
    friskluft = st.slider("GS5P101 – Friskluft (Forbrenning av støv) (%)", 0, 100, ai_friskluft)
    primluft = st.slider("GS5F101 – Primærluftsflekt (%)", 0, 100, ai_primluft)
    trykkovn = st.slider("G80GP101 – Trykk ovn (Pa)", -500, 0, ai_trykkovn)
    hombak = st.slider("Utmating Hombak (%)", 0, 100, ai_hombak if bruk_ai else 50)
    maier = st.slider("Utmating Maier (%)", 0, 100, ai_maier if bruk_ai else 50)

    st.divider()
    st.subheader("📐 Sensorjustering og prøvemåling")

    manual_fukt = st.number_input("Fuktighet tørrspon (målt prøve) (%)", 0.0, 10.0, step=0.01, value=1.20)
    sensor_fukt = st.number_input("Fuktighet tørrspon (sensorverdi) (%)", 0.0, 10.0, step=0.01, value=1.40)

    avvik = round(sensor_fukt - manual_fukt, 2)
    st.write(f"📏 Sensoren viser **{avvik:+.2f}%** i avvik fra virkelig målt verdi.")

    st.markdown("---")
    st.subheader("🔧 Estimer ny fukt ved temperaturjustering")

    utlopstemp = st.number_input("Nåværende utløpstemp. (G80GT106) °C", 100, 200, value=140)
    endring = st.slider("Still ned eller opp temp (grader)", -10, 10, step=1, value=0)
    ny_temp = utlopstemp + endring

    st.write(f"👉 Justert temperatur: **{ny_temp} °C**")
    forventet_fukt = manual_fukt + (endring * -0.06)
    st.success(f"Estimat: Ny fukt vil bli ca. **{forventet_fukt:.2f}%**")

# === HØYRE SIDE: RESULTAT ===
with col2:
    st.header("📈 Resultat")

    def beregn_fukt(g105, g106, frisk, prim, trykk, hombak, maier):
        return round(
            3.0
            - (g105 - 300) * 0.009
            - (g106 - 120) * 0.015
            + (frisk - 60) * 0.015
            + (prim - 30) * 0.012
            + ((trykk + 270) / 100) * 0.3
            + (hombak - 50) * 0.015
            + (maier - 50) * 0.03,
            2
        )

    fukt = beregn_fukt(temp_til, temp_ut, friskluft, primluft, trykkovn, hombak, maier)
    diff = round(fukt - target_fukt, 2)

    st.metric("🔹 Beregnet fukt", f"{fukt:.2f} %")
    st.metric("🎯 Ønsket fukt", f"{target_fukt:.2f} %")
    st.metric("➖ Avvik", f"{diff:+.2f} %")

    if temp_ut > 137 or temp_ut < 133:
        st.warning("⚠️ Utløpstemp utenfor mål for 22mm gulvplate (133–137 °C)")
    else:
        st.success("✅ Utløpstemp OK for 22mm gulvplate")

    if temp_til > 670:
        st.error("🔥 Innløpstemp overstiger 670 °C – for varmt!")

    if trykkovn != -270:
        st.warning("ℹ️ Trykk ovn avviker fra anbefalt -270 Pa")
    else:
        st.success("✅ Trykk ovn OK")

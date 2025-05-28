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

    st.write("✳️ AI-forslag fra kommando:")
    st.write(f"• Ønsket fukt: {ai_target_fukt} %")

    bruk_ai = st.checkbox("⚙️ Bruk AI-forslag i innstillingene", value=False)

    st.header("🧠 Smart justering: utløpstemp først, mating sekundært")
    st.caption("ℹ️ Normalt ligger fukt mellom 0.65–1.35 % når utløpstemp er 133–136 °C for 22mm gulvplate.")
    smartrun = st.button("🎯 Foreslå justeringer for å nå ønsket fukt")

    def beregn_fukt(g105, g106, frisk, prim, trykk, hombak, maier):
        return round(
            3.21
            - (g105 - 300) * 0.008
            - (g106 - 120) * 0.017
            + (frisk - 60) * 0.010
            + (prim - 30) * 0.012
            + ((trykk + 270) / 100) * 0.3
            + (hombak - 50) * 0.010
            + (maier - 50) * 0.005,
            2
        )

    smart_justering = ""

    if smartrun:
        nå_fukt = beregn_fukt(400, 135, 60, 30, -270, 50, 50)
        diff = round(ai_target_fukt - nå_fukt, 2)
        smart_justering = ""

        if abs(diff) < 0.05:
            smart_justering = "✅ Du er allerede nær ønsket fukt. Ingen justering trengs."
        else:
            if diff > 0:
                smart_justering += "🔼 Fukt er for lav – prøv dette:\n"
                smart_justering += "• Senk utløpstemp med 1 °C\n"
                smart_justering += "• Øk hombak-mating med 5 %\n"
            else:
                smart_justering += "🔽 Fukt er for høy – prøv dette:\n"
                smart_justering += "• Øk utløpstemp med 1 °C\n"
                smart_justering += "• Reduser hombak-mating med 5 %\n"

        st.code(smart_justering)

    st.header("🔧 Justeringer")

    target_fukt = st.number_input("Ønsket fukt (%)", 0.5, 4.0, step=0.01, value=ai_target_fukt if bruk_ai else 1.20)
    temp_til = st.slider("G80GT105 – Innløpstemp (°C)", 250, 700, ai_temp_til)
    temp_ut = st.slider("G80GT106 – Utløpstemp (°C)", 100, 180, ai_temp_ut)
    friskluft = st.slider("GS5P101 – Friskluft (Forbrenning av støv) (%)", 0, 100, ai_friskluft)
    primluft = st.slider("GS5F101 – Primærluftsflekt (%)", 0, 100, ai_primluft)
    trykkovn = st.slider("G80GP101 – Trykk ovn (Pa)", -500, 0, ai_trykkovn)
    hombak = st.slider("Utmating Hombak (%)", 0, 100, ai_hombak)
    maier = st.slider("Utmating Maier (%)", 0, 100, ai_maier)

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

import streamlit as st
import numpy as np

st.title("Fuktprognose – AI-styrt manuelt panel")

st.markdown("🧠 Fyll inn ønsket fukt – AI foreslår verdier. Du kan justere manuelt etterpå.")

# === Modell for fuktberegning ===
def beregn_fukt(g105, g106, frisk, prim, trykk, hombak, maier):
    return round(
        3.0
        - (g105 - 300) * 0.009
        - (g106 - 120) * 0.015
        + (frisk - 60) * 0.015
        + (prim - 30) * 0.012
        + ((trykk + 270) / 100) * 0.3
        + (hombak - 20) * 0.02
        + (maier - 20) * 0.04,
        2
    )

# === AI-FORSLAG BASERT PÅ ØNSKET FUKT ===
st.header("🧠 Ønsket fukt og AI-forslag")
target_fukt = st.number_input("Skriv ønsket fukt (%)", min_value=0.5, max_value=4.0, step=0.01, value=1.20)

beste_diff = 10
beste_kombinasjon = None

for g105 in range(350, 461, 5):
    for g106 in range(130, 161, 5):
        for frisk in range(45, 66, 3):
            for prim in range(20, 41, 3):
                for trykk in range(-290, -249, 5):
                    for hombak in range(10, 31, 5):
                        for maier in range(10, 31, 5):
                            fukt = beregn_fukt(g105, g106, frisk, prim, trykk, hombak, maier)
                            diff = abs(fukt - target_fukt)
                            if diff < beste_diff:
                                beste_diff = diff
                                beste_kombinasjon = (g105, g106, frisk, prim, trykk, hombak, maier, fukt)

# === SLIDERS: STARTER MED AI-FORSLAG ===
st.header("🛠 Manuell kontroll (AI-styrt startverdi)")

if beste_kombinasjon:
    ai_g105, ai_g106, ai_frisk, ai_prim, ai_trykk, ai_hombak, ai_maier, ai_fukt = beste_kombinasjon

    temp_til = st.slider("G80GT105 – Røykgasstemp. til tørk (°C)", 250, 500, ai_g105)
    temp_ut = st.slider("G80GT106 – Røykgasstemp. ut av tørk (°C)", 100, 180, ai_g106)
    friskluft = st.slider("GS5P101 – Friskluftspjeld (%)", 0, 100, ai_frisk)
    primluft = st.slider("GS5F101 – Primærluftsflekt (%)", 0, 100, ai_prim)
    trykkovn = st.slider("G80GP101 – Tryckugn (Pa)", -500, 0, ai_trykk)
    hombak_mating = st.slider("Hombak-mating (%)", 10, 40, ai_hombak)
    maier_mating = st.slider("Maier-mating (%)", 10, 40, ai_maier)

    # Oppdatert fukt etter manuell justering
    fukt_manuell = beregn_fukt(temp_til, temp_ut, friskluft, primluft, trykkovn, hombak_mating, maier_mating)

    st.subheader("📊 Oppdatert fuktprognose:")
    st.write(f"**{fukt_manuell} %**")

    if fukt_manuell > 2.5:
        st.error("⚠️ For høy fukt – vurder mindre mating eller mer varme.")
    elif fukt_manuell < 1.2:
        st.warning("⚠️ For tørr spon – vurder mer mating eller mindre varme.")
    else:
        st.success("✅ Fukt innenfor målområdet.")

else:
    st.warning("Fant ingen forslag – juster ønsket fukt eller verdier.")

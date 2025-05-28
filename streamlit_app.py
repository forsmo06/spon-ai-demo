import streamlit as st
import numpy as np

st.title("Fuktprognose – manuelt og automatisk")

st.markdown("Velg selv verdier, eller skriv ønsket fukt og få AI-forslag.")

# --- Del 1: Automatisk forslag basert på ønsket fukt ---
st.header("🧠 Automatisk forslag")

target_fukt = st.number_input("Skriv ønsket fukt (%)", min_value=0.5, max_value=4.0, step=0.01, value=1.20)

def beregn_fukt(g105, g106, frisk, prim, trykk):
    return round(
        3.0
        - (g105 - 300) * 0.009
        - (g106 - 120) * 0.015
        + (frisk - 60) * 0.015
        + (prim - 30) * 0.012
        + ((trykk + 270) / 100) * 0.3,
        2
    )

beste_diff = 10
beste_kombinasjon = None

for g105 in range(350, 461, 5):
    for g106 in range(130, 161, 5):
        for frisk in range(45, 66, 3):
            for prim in range(20, 41, 3):
                for trykk in range(-290, -249, 5):
                    fukt = beregn_fukt(g105, g106, frisk, prim, trykk)
                    diff = abs(fukt - target_fukt)
                    if diff < beste_diff:
                        beste_diff = diff
                        beste_kombinasjon = (g105, g106, frisk, prim, trykk, fukt)

if beste_kombinasjon:
    g105, g106, frisk, prim, trykk, fukt = beste_kombinasjon
    st.subheader("🔧 Forslag:")
    st.write(f"G80GT105 – Temp til tørk: **{g105} °C**")
    st.write(f"G80GT106 – Temp ut tørk: **{g106} °C**")
    st.write(f"GS5P101 – Friskluftspjeld: **{frisk} %**")
    st.write(f"GS5F101 – Primærluftsflekt: **{prim} %**")
    st.write(f"G80GP101 – Tryckugn: **{trykk} Pa**")
    st.success(f"Forventet fukt: **{fukt} %**")

# --- Del 2: Manuell styring ---
st.header("🛠 Manuell justering")

temp_til = st.slider("G80GT105 – Røykgasstemp. til tørk (°C)", 250, 500, 420)
temp_ut = st.slider("G80GT106 – Røykgasstemp. ut av tørk (°C)", 100, 180, 135)
friskluft = st.slider("GS5P101 – Friskluftspjeld (%)", 0, 100, 60)
primluft = st.slider("GS5F101 – Primærluftsflekt (%)", 0, 100, 30)
trykkovn = st.slider("G80GP101 – Tryckugn (Pa)", -500, 0, -270)

# Beregn fukt basert på manuelle verdier
fukt_manuell = beregn_fukt(temp_til, temp_ut, friskluft, primluft, trykkovn)
st.subheader("📊 Beregnet fukt (manuell):")
st.write(f"**{fukt_manuell} %**")

if fukt_manuell > 2.5:
    st.error("⚠️ For høy fukt – vurder mer varme eller mindre friskluft.")
elif fukt_manuell < 1.2:
    st.warning("⚠️ For tørr spon – vurder å senke tørkekraft eller øke friskluft.")
else:
    st.success("✅ Fukt innenfor målområde.")

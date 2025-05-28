import streamlit as st

st.title("Fuktprognose – med IPAAR-sensorer")

st.markdown("Estimat av sponfukt etter tørke basert på sensorverdier fra ovn og tørk.")

# Sensorinput
temp_ugn_topp = st.slider("G80GT103 – Temp topp ugn (°C)", 600, 1000, 883)
temp_ugn_indre = st.slider("G80GT101 – Temp indre ugn (°C)", 600, 900, 779)
temp_til_tork = st.slider("G80GT105 – Røyktemp til tørk (°C)", 250, 500, 420)
temp_ut_tork = st.slider("G80GT106 – Røyktemp ut av tørk (°C)", 100, 180, 135)
friskluft = st.slider("GS5P101 – Friskluftspjeld (%)", 0, 100, 67)
ugnstrykk = st.slider("G80PC102 – Ugnstrykk (kPa)", -5.0, 0.0, -2.7)
primærluft = st.slider("GS5F101 – Primærluftsflekt (%)", 0, 100, 26)

# Fuktmodell (forenklet)
fukt = round(
    3.0
    - (temp_til_tork - 300) * 0.009
    - (temp_ut_tork - 120) * 0.015
    + (friskluft - 60) * 0.015
    + (primærluft - 30) * 0.012
    + (ugnstrykk + 2.5) * 0.3,
    2
)

st.write(f"### Beregnet fukt etter tørke: **{fukt} %**")

# Vurdering
if temp_til_tork > 460:
    st.warning("🚨 Høy røykgasstemperatur – vanninnsprøytning kan slå inn.")
if ugnstrykk > -1.0:
    st.warning("⚠️ Lavt undertrykk – mulig dårlig trekk i ovn.")
if fukt > 2.5:
    st.error("⚠️ For høy fukt – vurder mer varme eller mindre luft.")
elif fukt < 1.2:
    st.warning("⚠️ For tørr spon – vurder mer friskluft eller senk temperatur.")
else:
    st.success("✅ Fukt ligger innenfor målet.")

st.caption("Sensorer: G80GTxxx, G80PC102, GS5P101, GS5F101. Neste steg: koble til ekte AI.")

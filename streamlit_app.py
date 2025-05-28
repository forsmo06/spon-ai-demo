import streamlit as st

st.title("Fuktprognose – med faktiske IPAAR-sensorer")

st.markdown("Basert på sensorer fra flisfyr og tørkestyring.")

# Sensorverdier fra anlegget
temp_ugn_topp = st.slider("G80GT103 – Temp topp ugn (°C)", 600, 1000, 883)
temp_ugn_indre = st.slider("G80GT101 – Temp indre ugn (°C)", 600, 900, 779)
temp_til_tork = st.slider("G80GT105 – Røyktemp til tørk (°C)", 250, 500, 420)
temp_ut_tork = st.slider("G80GT106 – Røyktemp ut av tørk (°C)", 100, 180, 135)
friskluft = st.slider("GS5P101 – Friskluftspjeld (%)", 0, 100, 67)

# Forenklet kalkulasjon av fukt
fukt = round(
    3.0
    - (temp_til_tork - 300) * 0.01
    - (temp_ut_tork - 120) * 0.02
    + (friskluft - 60) * 0.015,
    2
)

st.write(f"### Beregnet fukt etter tørke: **{fukt} %**")

# Vurdering
if temp_til_tork > 460:
    st.warning("🚨 Høy røykgasstemperatur – vanninnsprøytning kan slå inn.")
if fukt > 2.5:
    st.error("⚠️ For høy fukt – vurder mer varme eller mindre friskluft.")
elif fukt < 1.2:
    st.warning("⚠️ For tørr spon – vurder mer friskluft eller lavere temperatur.")
else:
    st.success("✅ Fukt ser stabil ut.")

st.caption("Bruker faktisk sensor-ID fra IPAAR. Neste steg: Ekte AI basert på produksjonsdata.")

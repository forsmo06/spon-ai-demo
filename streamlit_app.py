import streamlit as st

st.title("Fuktprognose – basert på IPAAR-data")

st.markdown("Estimat av sponfukt etter tørke, basert på sanntidsverdier fra tørke og forbrenning.")

# Sensorinput
temp_ugn_topp = st.slider("G80GT103 – Temp topp ugn (°C)", 600, 1000, 883)
temp_ugn_indre = st.slider("G80GT101 – Temp indre ugn (°C)", 600, 900, 779)
temp_til_tork = st.slider("G80GT105 – Røykgasstemp. til tørk (°C)", 250, 500, 420)
temp_ut_tork = st.slider("G80GT106 – Røykgasstemp. ut av tørk (°C)", 100, 180, 135)
friskluft = st.slider("GS5P101 – Friskluftspjeld (%)", 0, 100, 67)
primærluft = st.slider("GS5F101 – Primærluftsflekt (%)", 0, 100, 26)
trykk_ovn = st.slider("G80GP101 – Tryckugn (Pa)", -500, 0, -270)

# Forenklet beregningsmodell
fukt = round(
    3.0
    - (temp_til_tork - 300) * 0.009
    - (temp_ut_tork - 120) * 0.015
    + (friskluft - 60) * 0.015
    + (primærluft - 30) * 0.012
    + ((trykk_ovn + 270) / 100) * 0.3,  # sentrert rundt -270 Pa
    2
)

st.write(f"### Beregnet fukt etter tørke: **{fukt} %**")

# Varslinger
if temp_til_tork > 460:
    st.warning("🚨 Høy røykgasstemperatur – vannsprøyting kan slå inn.")
if trykk_ovn > -100:
    st.warning("⚠️ Svakt undertrykk – sjekk trekk, spjeld eller forbrenning.")
if fukt > 2.5:
    st.error("⚠️ For høy fukt – vurder mindre friskluft eller høyere temp.")
elif fukt < 1.2:
    st.warning("⚠️ For tørr spon – vurder å senke tørkekraft eller øke friskluft.")
else:
    st.success("✅ Fuktverdi er innenfor målområdet.")

st.caption("Sensorverdier: G80GTxxx, GS5P101, GS5F101, G80GP101 (Pa). Neste steg: AI-trening.")

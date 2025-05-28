import streamlit as st

st.title("Fuktprognose – basert på IPAAR-data")

st.markdown("Bruk faktiske verdier fra IPAAR for å estimere sponfukt etter tørke.")

# Sensorverdier fra bildet
temp_rist = st.slider("GG9T101 – Temp. etter rist (°C)", 300, 500, 355)
temp_røyk = st.slider("G80GT105 – Røykgastemp. før tørk (°C)", 100, 200, 132)
temp_blkamm = st.slider("GG9T102 – Temp. blandkammer (°C)", 800, 1100, 972)
o2 = st.slider("GG9O101 – O2 i røykgass (%)", 5.0, 20.0, 12.5)
friskluft_spjeld = st.slider("GS5P101 – Friskluftspjeld (%)", 0, 100, 65)

# Forenklet fuktmodell
fukt = round(
    3.2
    - (temp_rist - 340) * 0.003
    - (temp_røyk - 120) * 0.03
    - (o2 - 10) * 0.02
    + (friskluft_spjeld - 60) * 0.01,
    2
)

st.write(f"### Beregnet fukt etter tørke: **{fukt} %**")

# Anbefaling
if fukt > 2.5:
    st.error("⚠️ For høy fukt – vurder å redusere friskluft eller øke røykgasstemperatur.")
elif fukt < 1.2:
    st.warning("⚠️ For tørr spon – vurder å øke friskluft eller senke tørkevarme.")
else:
    st.success("✅ Fukt ligger innenfor normalområde.")

st.caption("Denne beregningen er forenklet. Neste steg er å trene en AI-modell på faktiske produksjonsdata.")

               

import streamlit as st

st.title("Fuktprognose – basert på IPAAR-data")

st.markdown("Bruk faktiske prosessverdier fra flisfyr og tørke for å estimere sponfuktighet etter tørk.")

# Faktiske sensorfelt fra IPAAR
temp_rist = st.slider("GG9T101 – Temperatur etter rist (°C)", 300, 500, 355)
temp_til_tork = st.slider("GG9T106 – Temperatur til tørk (°C)", 100, 160, 132)
temp_blkamm = st.slider("GG9T102 – Temperatur blandkammer (°C)", 800, 1100, 972)
o2 = st.slider("GG9O101 – Røykgass O2 (%)", 5.0, 20.0, 12.5)
friskluft_spjeld = st.slider("GS5P101 – Friskluftspjeld (%)", 0, 100, 65)

# Forenklet fuktmodell
fukt = round(
    3.2
    - (temp_rist - 340) * 0.003
    - (temp_til_tork - 120) * 0.03
    - (o2 - 10) * 0.02
    + (friskluft_spjeld - 60) * 0.01,
    2
)

st.write(f"### Beregnet fukt etter tørke: **{fukt} %**")

if fukt > 2.5:
    st.error("⚠️ For høy fukt – vurder å redusere friskluft eller øke varme.")
elif fukt < 1.2:
    st.warning("⚠️ For tørr spon – vurder å øke friskluft eller senke temperatur.")
else:
    st.success("✅ Fukt ser fin ut!")

st.ca

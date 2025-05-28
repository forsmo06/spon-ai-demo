import streamlit as st
import numpy as np

st.title("Fuktprognose og sensorjustering")

st.markdown("🧪 Skriv inn både manuell fuktmåling og sensorverdi for å se avvik og få justeringsforslag.")

# === Input: Manuell og sensorfukt ===
manual_fukt = st.number_input("Manuell fuktmåling (%)", min_value=0.0, max_value=10.0, value=1.20, step=0.01)
sensor_fukt = st.number_input("Sensorverdi fuktighet (%)", min_value=0.0, max_value=10.0, value=1.40, step=0.01)

# === Beregn avvik ===
avvik = round(sensor_fukt - manual_fukt, 2)
st.write(f"📏 Sensoren viser **{avvik:+.2f}%** i avvik fra virkelig målt verdi.")

# === Ønsket fukt og antatt justering ===
st.markdown("---")
st.header("🔧 Justering for ønsket fukt")

oensket_fukt = st.number_input("Ønsket fukt etter ny justering (%)", min_value=0.0, max_value=10.0, value=1.20, step=0.01)

st.markdown("Angi dagens utgående røykgasstemperatur og hvor mye du vil justere:")
utlopstemp = st.number_input("Nåværende utgående temp etter tørk (G80GT106) °C", min_value=100, max_value=200, value=140)
endring = st.slider("Still ned eller opp temp (grader)", -10, 10, step=1, value=0)

ny_temp = utlopstemp + endring
st.write(f"👉 Justert temperatur: **{ny_temp} °C**")

# Simulert formel: Lavere temp = høyere fukt
forventet_fukt = manual_fukt + (endring * -0.06)  # hver grad gir ca. 0.06 % effekt
st.success(f"Estimat: Ny fukt vil bli ca. **{forventet_fukt:.2f}%**")

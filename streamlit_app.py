import streamlit as st
import numpy as np

st.title("Fuktprognose med automatisk innstillingsforslag")

st.markdown("🧪 Basert på ønsket fuktighet finner systemet de mest passende innstillingene.")

# Ønsket fukt
target_fukt = st.number_input("Skriv inn ønsket fukt etter tørke (%)", min_value=0.5, max_value=4.0, step=0.01, value=1.20)

# Modellberegning
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

# Søk etter beste kombinasjon
beste_diff = 10
beste_kombinasjon = None

for g105 in range(350, 461, 5):       # Røyktemp til tørk
    for g106 in range(130, 161, 5):   # Røyktemp ut tørk
        for frisk in range(45, 66, 3):
            for prim in range(20, 41, 3):
                for trykk in range(-290, -249, 5):
                    fukt = beregn_fukt(g105, g106, frisk, prim, trykk)
                    diff = abs(fukt - target_fukt)
                    if diff < beste_diff:
                        beste_diff = diff
                        beste_kombinasjon = (g105, g106, frisk, prim, trykk, fukt)

# Vis forslag
if beste_kombinasjon:
    g105, g106, frisk, prim, trykk, fukt = beste_kombinasjon
    st.subheader("🔧 Forslag til innstillinger:")
    st.write(f"G80GT105 – Temp til tørk: **{g105} °C**")
    st.write(f"G80GT106 – Temp ut av tørk: **{g106} °C**")
    st.write(f"GS5P101 – Friskluftspjeld: **{frisk} %**")
    st.write(f"GS5F101 – Primærluft: **{prim} %**")
    st.write(f"G80GP101 – Tryckugn: **{trykk} Pa**")
    st.success(f"👉 Forventet fukt: **{fukt} %**")

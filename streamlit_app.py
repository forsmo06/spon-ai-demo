import streamlit as st

st.title("AI-styring: Flisfyr og tørke")

# --- Inputdata fra bruker eller sensorer ---
trykk = st.number_input("Trykk i ovn (Pa)", value=280)
utlopstemp = st.number_input("Utløpstemperatur (°C)", value=132.0)
friskluft = st.slider("Friskluftspjeld (%)", 0, 100, 85)
primaerluft = st.slider("Primærluftsflakt (%)", 0, 100, 70)

# --- Målverdier ---
ønsket_trykk = 270
ønsket_utlopstemp = 134

# --- AI-beregning (regelbasert versjon først) ---
def ai_foreslaa(trykk, utlopstemp, friskluft, primaerluft):
    justering_friskluft = 0
    justering_primaerluft = 0

    if trykk > ønsket_trykk + 10:
        justering_friskluft = +5
        justering_primaerluft = -3
    elif trykk < ønsket_trykk - 10:
        justering_friskluft = -5
        justering_primaerluft = +3

    if utlopstemp < ønsket_utlopstemp - 1:
        justering_primaerluft += 4
    elif utlopstemp > ønsket_utlopstemp + 1:
        justering_primaerluft -= 4

    # Forslag, begrenset mellom 0–100 %
    ny_friskluft = max(0, min(100, friskluft + justering_friskluft))
    ny_primaerluft = max(0, min(100, primaerluft + justering_primaerluft))

    return ny_friskluft, ny_primaerluft

# --- Kjør forslag ---
forslag_friskluft, forslag_primaerluft = ai_foreslaa(trykk, utlopstemp, friskluft, primaerluft)

st.subheader("AI-forslag:")
st.write(f"👉 Justér friskluftspjeld til **{forslag_friskluft:.0f} %**")
st.write(f"👉 Justér primærluft til **{forslag_primaerluft:.0f} %**")


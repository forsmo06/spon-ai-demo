import streamlit as st

st.title("Sponfukt-forutsigelse – Prototype")

st.markdown("Fyll inn dagens verdier fra tørka, og få en AI-lignende anbefaling.")

# Input-felter
maier = st.slider("Maier-mating (%)", 10, 40, 25)
brennkammer = st.slider("Brennkammer-temp (°C)", 800, 1000, 900)
utlop_temp = st.slider("Utløpstemperatur (°C)", 100, 150, 130)
fyring = st.slider("Fyringsnivå (%)", 0, 100, 70)

# En enkel regelbasert prediksjon
fukt = round(3.5 - (brennkammer - 800) * 0.003 - (utlop_temp - 120) * 0.02 - (fyring * 0.01) + (maier - 20) * 0.04, 2)

st.write(f"### Beregnet fukt etter tørke: **{fukt} %**")

# Anbefaling
if fukt > 2.5:
    st.error("⚠️ For høy fukt – vurder å senke mating eller øke fyring.")
elif fukt < 1.2:
    st.warning("⚠️ For tørr spon – vurder å redusere tørking for å spare energi.")
else:
    st.success("✅ Fukt ser bra ut!")

st.caption("Dette er en prototype – basert på forenklet modell uten ekte AI (enda).")
import streamlit as st

st.title("🎈 My new app")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)

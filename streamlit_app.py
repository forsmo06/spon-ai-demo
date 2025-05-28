import streamlit as st

st.set_page_config(page_title="Flisfyr Demo", layout="wide")

# Bakgrunnsbilde som base
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{st.image("017d7937-301e-449e-871a-755d160c2954.png")}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        height: 100vh;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🔥 Flisfyringsdashboard - Demo")

# Temperatur-visning (kan oppdateres dynamisk)
temp = st.slider("Brennkammertemperatur (°C)", 600, 1100, 870)
st.markdown(f"<h1 style='color: orange; text-align:center;'>{temp}°C</h1>", unsafe_allow_html=True)

# Statuslamper
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"<div style='background-color: {'green' if temp > 800 else 'red'}; color: white; padding: 10px; text-align:center;'>Brennkammertemp</div>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<div style='background-color: green; color: white; padding: 10px; text-align:center;'>Trykk ovn: -270 Pa</div>", unsafe_allow_html=True)
with col3:
    st.markdown(f"<div style='background-color: green; color: white; padding: 10px; text-align:center;'>Friskluft: 12%</div>", unsafe_allow_html=True)

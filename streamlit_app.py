import streamlit as st
import base64

# Les inn bildet og konverter til base64-streng
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

image_path = "017d7937-301e-449e-871a-755d160c2954.png"  # Pass på at bildet ligger i samme mappe som koden
img_base64 = get_base64_of_bin_file(image_path)

st.set_page_config(page_title="Flisfyr Demo", layout="wide")

# Sett bakgrunnsbildet i CSS
page_bg_img = f"""
<style>
.stApp {{
    background-image: url("data:image/png;base64,{img_base64}");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    height: 100vh;
}}
</style>
"""

st.markdown(page_bg_img, unsafe_allow_html=True)

st.title("🔥 Flisfyringsdashboard - Demo")

temp = st.slider("Brennkammertemperatur (°C)", 600, 1100, 870)
st.markdown(f"<h1 style='color: orange; text-align:center;'>{temp}°C</h1>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"<div style='background-color: {'green' if temp > 800 else 'red'}; color: white; padding: 10px; text-align:center;'>Brennkammertemp</div>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<div style='background-color: green; color: white; padding: 10px; text-align:center;'>Trykk ovn: -270 Pa</div>", unsafe_allow_html=True)
with col3:
    st.markdown(f"<div style='background-color: green; color: white; padding: 10px; text-align:center;'>Friskluft: 12%</div>", unsafe_allow_html=True)

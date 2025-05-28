import streamlit as st
import base64

# Funksjon for å lese bilde og konvertere til base64
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Sti til bildet ditt
image_path = 'd84f4086-7c88-4aeb-9eb0-6a0cc8b79dd8.png'

img_base64 = get_base64_of_bin_file(image_path)

page_bg_img = f'''
<style>
[data-testid="stAppViewContainer"] {{
background-image: url("data:image/png;base64,{img_base64}");
background-size: cover;
background-position: center;
background-repeat: no-repeat;
background-attachment: fixed;
}}
</style>
'''

st.markdown(page_bg_img, unsafe_allow_html=True)

# Her kan du legge på resten av app-koden din
st.title("Flisfyringsdashboard - Demo")

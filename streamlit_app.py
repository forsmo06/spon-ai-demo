import streamlit as st
import base64

uploaded_file = st.file_uploader("Last opp bakgrunnsbilde (png)")

if uploaded_file is not None:
    img_bytes = uploaded_file.read()
    img_base64 = base64.b64encode(img_bytes).decode()
else:
    st.warning("Vennligst last opp bakgrunnsbildet.")
    st.stop()

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

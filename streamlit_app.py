import streamlit as st
import base64

# Funksjon for å lese bilde og konvertere til base64
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Sett inn ditt bildefilnavn her (må være lastet opp i prosjektmappa)
image_path = 'd84f4086-7c88-4aeb-9eb0-6a0cc8b79dd8.png'
img_base64 = get_base64_of_bin_file(image_path)

# CSS for bakgrunnsbilde
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

# App tittel
st.title("🔧 Flisfyringsdashboard - Demo")

# Layout med tre kolonner
col1, col2, col3 = st.columns([3, 1, 2])

with col1:
    st.subheader("Flisfyringsovn")
    st.markdown("""
    <div style='
        width: 300px; height: 400px; 
        background: linear-gradient(to bottom, #555, #222);
        border-radius: 20px; padding: 20px; color: white; font-weight: bold;
        display: flex; flex-direction: column; justify-content: center; align-items: center;
        box-shadow: 0 0 15px #ff7e00;
        '>
        🔥 <br> Temperatur<br><span style='font-size: 40px;'>{temp}°C</span>
    </div>
    """.format(temp=st.session_state.get('temp', 790)), unsafe_allow_html=True)

with col2:
    st.subheader("Statuslamper")

    def lampe(navn, verdi, min_ok, max_ok):
        farge = "green" if min_ok <= verdi <= max_ok else "red"
        st.markdown(f"<div style='background:{farge}; padding:10px; border-radius:10px; margin-bottom:10px; color:white;'>{navn}: {verdi}</div>", unsafe_allow_html=True)

    temp = st.session_state.get('temp', 790)
    lampe("Brennkammertemp", temp, 600, 1000)
    lampe("Trykk ovn", st.session_state.get('trykk_ovn', -270), -500, 0)
    lampe("Friskluft", st.session_state.get('friskluft', 12), 0, 100)

with col3:
    st.subheader("Juster parametre")

    temp = st.slider("Brennkammertemp (°C)", 600, 1000, st.session_state.get('temp', 790))
    friskluft = st.slider("Friskluft (%)", 0, 100, st.session_state.get('friskluft', 12))
    trykk_ovn = st.slider("Trykk ovn (Pa)", -500, 0, st.session_state.get('trykk_ovn', -270))

    # Oppdater session_state slik at verdier vises live
    st.session_state['temp'] = temp
    st.session_state['friskluft'] = friskluft
    st.session_state['trykk_ovn'] = trykk_ovn

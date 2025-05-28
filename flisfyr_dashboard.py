import streamlit as st

st.set_page_config(page_title="Flisfyringsdashboard", layout="wide")

st.title("🛠️ Flisfyringsdashboard - Demo")

# Layout i tre kolonner: ovn, statuslamper, justeringer
col1, col2, col3 = st.columns([3, 1, 2])

with col1:
    st.subheader("Flisfyringsovn")
    st.markdown("""
    <div style='
        width: 300px; height: 400px; 
        background: linear-gradient(to bottom, #555, #222);
        border-radius: 20px; padding: 20px; color: white; font-weight: bold;
        display: flex; flex-direction: column; justify-content: center; align-items: center;
        box-shadow: 0 0 15px #ff7e00;'>
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

    # Oppdaterer session state
    st.session_state['temp'] = temp
    st.session_state['friskluft'] = friskluft
    st.session_state['trykk_ovn'] = trykk_ovn

st.markdown("---")
st.write("⚠️ Dette er bare en enkel demo for å vise hvordan man kan lage et mer levende dashbord. Du kan legge til flere komponenter og data etter behov.")

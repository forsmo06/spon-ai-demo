import streamlit as st

st.title("Demo flisfyr med piler og statuslamper")

# Statuslampe eksempel
def lampe(name, status):
    farge = "green" if status == "ok" else "red"
    st.markdown(f"""
    <div style='
        background-color:{farge}; 
        width:100px; height:30px; border-radius:10px; 
        color:white; text-align:center; line-height:30px;
        margin-bottom:10px;'>{name}: {status}</div>
    """, unsafe_allow_html=True)

lampe("Flismatning", "ok")
lampe("Lufttrykk", "feil")

# En pil med farge basert på status
status = "ok"
farge_pil = "green" if status == "ok" else "red"

st.markdown(f"""
<div style="font-size:30px; color:{farge_pil};">
    &#8594; Luft flyter her
</div>
""", unsafe_allow_html=True)

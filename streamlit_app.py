import streamlit as st

st.set_page_config(layout="wide")
st.title("💬 Hjelp – AI-chat for operatør")

# Start chat-historikk
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Enkel svarfunksjon med manuelle svar
def hent_svar_fra_manual(sporsmal):
    s = sporsmal.lower()
    if "utløpstemp" in s:
        return "Utløpstemp er temperaturen etter tørka. Den påvirker fuktigheten i spona."
    elif "loggføre" in s:
        return "For å loggføre en prøve, still inn verdiene og trykk på 'Loggfør denne prøven'-knappen."
    elif "fukt for lav" in s or "fukta for lav" in s:
        return "Hvis fukta er for lav, kan du senke utløpstemp eller redusere friskluft/innmating."
    elif "starte tørka" in s:
        return "Sjekk at systemet er i auto, og at alle verdier er innenfor grenser før du starter."
    elif "hombak" in s:
        return "Hombak er innmatingen for tørr spon. Juster den i prosent etter behov."
    elif "maier" in s:
        return "Maier er innmatingen for fuktig sagflis. Brukes mer ved lav innløpstemp."
    elif "trykk" in s:
        return "Trykk i ovnen skal ligge rundt -270 Pa. Går det mye utenfor, si ifra."
    else:
        return "Beklager, jeg forsto ikke spørsmålet helt. Prøv å stille det på en litt annen måte."

# Bruker skriver inn spørsmål
user_input = st.chat_input("Still et spørsmål om programmet her...")
if user_input:
    svar = hent_svar_fra_manual(user_input)
    st.session_state.chat_history.append(("👤 Du", user_input))
    st.session_state.chat_history.append(("🤖 Hjelperen", svar))

# Vis hele chatten
for rolle, melding in st.session_state.chat_history:
    st.chat_message(rolle).write(melding)

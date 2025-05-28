import pandas as pd
import os

FILENAME = "fuktlogg.csv"  # Navnet på CSV-filen som prøvene lagres i

def lagre_prove(data):
    """
    Logger en ny prøve til CSV-fil.
    Data må være en dict med kolonnenavn som nøkler.
    """
    df_ny = pd.DataFrame([data])
    
    if os.path.exists(FILENAME):
        df_eksisterende = pd.read_csv(FILENAME)
        df = pd.concat([df_eksisterende, df_ny], ignore_index=True)
    else:
        df = df_ny
        
    df.to_csv(FILENAME, index=False)
    print(f"Prøve lagret! Totalt antall prøver: {len(df)}")


# Eksempel på hvordan funksjonen kan brukes:
if __name__ == "__main__":
    ny_prøve = {
        "timestamp": "2025-05-28T08:40:00",
        "ønsket_fukt": 1.36,
        "beregnet_fukt": 1.25,
        "brennkammertemp": 790,
        "innløpstemp": 400,
        "utløpstemp": 135,
        "friskluft": 12,
        "primluft": 3,
        "trykkovn": -270,
        "hombak": 78,
        "maier": 25
    }
    lagre_prove(ny_prøve)

import pandas as pd
import os

FILENAME = "test_logg.csv"

def logg_data(data):
    df = pd.DataFrame([data])
    if os.path.exists(FILENAME):
        df_existing = pd.read_csv(FILENAME)
        df = pd.concat([df_existing, df], ignore_index=True)
    df.to_csv(FILENAME, index=False)
    print(f"Data logget. Antall rader nå: {len(df)}")

# Test data som legges til
ny_data = {
    "tid": "2025-05-28T08:00:00",
    "verdi": 42,
}

logg_data(ny_data)

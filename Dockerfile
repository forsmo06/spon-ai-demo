# 1) Bruk en lettvekts Python-base
FROM python:3.9-slim

# 2) Oppdater apt og installer Tesseract OCR-motoren
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        tesseract-ocr \
        libtesseract-dev \
    && rm -rf /var/lib/apt/lists/*

# 3) Sett arbeidskatalogen i containeren
WORKDIR /app

# 4) Kopier requirements.txt og installer Python-avhengigheter
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 5) Kopier resten av Streamlit-appen inn i containeren
COPY . .

# 6) Start Streamlit-appen på port 8080
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8080", "--server.address=0.0.0.0"]

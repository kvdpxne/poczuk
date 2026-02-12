# Oficjalny, minimalny obraz Python 3.13
FROM python:3.13-slim

# Ustaw katalog roboczy
WORKDIR /app

# Skopiuj plik zależności i zainstaluj biblioteki
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Skopiuj resztę kodu źródłowego
COPY . .

# Uruchom bota
CMD ["python", "main.py"]
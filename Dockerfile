# ETAP 1: Builder
# Wykorzystujemy lekki obraz Alpine do przygotowania zależności
FROM python:3.11-alpine AS builder

# Ustawienie katalogu roboczego
WORKDIR /app

# Kopiowanie wyłącznie pliku wymagań - optymalizacja cache'a (warstwa przebuduje się tylko gdy zmienimy wymagania)
COPY requirements.txt .

# Instalacja zależności do przestrzeni użytkownika, aby łatwo je skopiować w kolejnym etapie
RUN pip install --user --no-cache-dir -r requirements.txt

# ETAP 2: Obraz Docelowy (Runner)
# Wykorzystujemy ten sam lekki obraz bazy
FROM python:3.11-alpine

# Deklaracja autora zgodna ze standardem OCI
LABEL org.opencontainers.image.authors="Imię Nazwisko"

# Ustawienie katalogu roboczego
WORKDIR /app

# Kopiowanie zainstalowanych pakietów z etapu buildera (wieloetapowe budowanie - oszczędność miejsca)
COPY --from=builder /root/.local /root/.local

# Kopiowanie kodu aplikacji
COPY app.py .

# Zapewnienie, że skrypty zainstalowane przez pip są widoczne w zmiennej PATH
ENV PATH=/root/.local/bin:$PATH
ENV PORT=8080

# Informacja dla Dockera o nasłuchującym porcie
EXPOSE $PORT

# Konfiguracja instrukcji healthcheck - weryfikuje czy aplikacja prawidłowo odpowiada
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost:$PORT/ || exit 1

# Uruchomienie aplikacji
CMD ["python", "app.py"]
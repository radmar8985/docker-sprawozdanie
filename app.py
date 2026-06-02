import os
import sys
from datetime import datetime
from flask import Flask, request, render_template_string
import requests

app = Flask(__name__)

# Konfiguracja danych autora i portu
AUTHOR = "Imię Nazwisko" # Wpisz tutaj swoje dane
PORT = int(os.environ.get("PORT", 8080))

# Predefiniowana lista lokalizacji wraz ze współrzędnymi geograficznymi (szerokość, długość)
LOCATIONS = {
    "Polska": {
        "Warszawa": (52.2297, 21.0122),
        "Kraków": (50.0647, 19.9450)
    },
    "Hiszpania": {
        "Madryt": (40.4168, -3.7038),
        "Barcelona": (41.3874, 2.1686)
    }
}

# Szablon HTML dla interfejsu użytkownika
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head><title>Aplikacja Pogodowa</title></head>
<body>
    <h2>Sprawdź pogodę</h2>
    <form method="POST">
        <label>Kraj:</label>
        <select name="country">
            {% for country in locations.keys() %}
            <option value="{{ country }}">{{ country }}</option>
            {% endfor %}
        </select>
        <br><br>
        <label>Miasto:</label>
        <select name="city">
            <option value="Warszawa">Warszawa</option>
            <option value="Kraków">Kraków</option>
            <option value="Madryt">Madryt</option>
            <option value="Barcelona">Barcelona</option>
        </select>
        <br><br>
        <input type="submit" value="Sprawdź">
    </form>
    
    {% if weather_data %}
        <h3>Pogoda dla: {{ selected_city }}, {{ selected_country }}</h3>
        <p>Temperatura: {{ weather_data['temperature'] }} °C</p>
        <p>Prędkość wiatru: {{ weather_data['windspeed'] }} km/h</p>
    {% endif %}
</body>
</html>
"""

# Funkcja uruchamiana przed pierwszym żądaniem
def log_startup_info():
    """Pozostawia w logach informację o dacie uruchomienia, autorze i porcie TCP"""
    startup_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Używamy flush=True, aby upewnić się, że logi natychmiast trafią do standardowego wyjścia w Dockerze
    print("=========================================", flush=True)
    print(f"Data uruchomienia kontenera: {startup_time}", flush=True)
    print(f"Autor programu: {AUTHOR}", flush=True)
    print(f"Aplikacja nasłuchuje na porcie TCP: {PORT}", flush=True)
    print("=========================================", flush=True)

log_startup_info()

@app.route("/", methods=["GET", "POST"])
def index():
    """Główny endpoint obsługujący formularz wyboru kraju/miasta i odpytujący API pogodowe"""
    weather_data = None
    selected_country = None
    selected_city = None

    if request.method == "POST":
        selected_country = request.form.get("country")
        selected_city = request.form.get("city")
        
        # Weryfikacja, czy wybrane miasto pasuje do predefiniowanej listy w danym kraju
        if selected_country in LOCATIONS and selected_city in LOCATIONS[selected_country]:
            lat, lon = LOCATIONS[selected_country][selected_city]
            
            # Pobieranie aktualnej pogody z darmowego Open-Meteo API
            api_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
            response = requests.get(api_url)
            
            if response.status_code == 200:
                weather_data = response.json().get("current_weather")
    
    return render_template_string(
        HTML_TEMPLATE, 
        locations=LOCATIONS, 
        weather_data=weather_data,
        selected_country=selected_country,
        selected_city=selected_city
    )

if __name__ == "__main__":
    # Uruchomienie serwera aplikacji
    app.run(host="0.0.0.0", port=PORT)
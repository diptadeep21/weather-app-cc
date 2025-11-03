from flask import Flask, render_template, request
import requests
import var
import os

app = Flask(__name__)

def get_weather(api_key, city):
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': city,
        'appid': api_key,
        'units': 'metric'
    }

    try:
        response = requests.get(base_url, params=params, timeout=10)
        data = response.json()

        if response.status_code == 200:
            return { 'ok': True, 'data': data }
        else:
            # OpenWeather often returns useful 'message' text in body
            message = data.get('message', 'Unable to fetch weather data') if isinstance(data, dict) else 'Unable to fetch weather data'
            return { 'ok': False, 'error': f"{response.status_code}: {message}" }

    except requests.Timeout:
        return { 'ok': False, 'error': 'Request timed out. Please try again.' }
    except Exception as e:
        return { 'ok': False, 'error': 'Unexpected error fetching weather data.' }

@app.route('/', methods=['GET', 'POST'])
def index():
    error = None
    weather_payload = None

    if request.method == 'POST':
        city = (request.form.get('city') or '').strip()

        # Prefer environment variable, fallback to var.py
        api_key = os.environ.get('OPENWEATHER_API_KEY') or getattr(var, 'key', '')

        if not api_key:
            error = 'API key is not configured.'
        elif not city:
            error = 'Please enter a city name.'
        else:
            result = get_weather(api_key, city)
            if result.get('ok'):
                weather_payload = result.get('data')
            else:
                error = result.get('error')

    # Extract weather condition for animations
    weather_condition = None
    if weather_payload and 'weather' in weather_payload and len(weather_payload['weather']) > 0:
        weather_condition = weather_payload['weather'][0]['main'].lower()
    
    return render_template('index.html', weather_data=weather_payload, error=error, weather_condition=weather_condition)

if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 8080)), host='0.0.0.0', debug=True)


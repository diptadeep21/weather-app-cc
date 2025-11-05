from flask import Flask, render_template, request, jsonify, redirect, url_for
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

def build_agriculture_recommendation(crop: str, temperature: float, humidity: float, rainfall: float):
    alerts = []
    # Alerts
    try:
        t = float(temperature)
        h = float(humidity)
        r = float(rainfall)
    except Exception:
        t, h, r = 0.0, 0.0, 0.0

    if h > 85:
        alerts.append('High humidity — fungal disease risk')
    if t <= 2:
        alerts.append('Frost risk ahead')
    if t >= 40:
        alerts.append('Extreme heat — heat stress risk')

    # Rule-based recommendation
    recommendation = 'Conditions are suitable for healthy crop growth.'
    if crop == 'Rice' and r > 20:
        recommendation = 'Ideal conditions for rice growth.'
    elif crop == 'Wheat' and t > 35:
        recommendation = 'Too hot for wheat — consider irrigation.'
    elif crop == 'Maize' and t < 15:
        recommendation = 'Low temperature — delayed germination possible.'
    elif crop == 'Cotton' and h > 80:
        recommendation = 'High humidity — monitor for pests and disease.'
    elif crop == 'Sugarcane' and r < 5 and t > 32:
        recommendation = 'Dry and hot — increase irrigation frequency.'
    elif h > 85:
        recommendation = 'High humidity — fungal disease risk.'

    # Specialized suggestions
    irrigation = 'Maintain current irrigation schedule.'
    if r < 3 and t > 32:
        irrigation = 'Increase irrigation frequency due to hot and dry conditions.'
    elif r >= 10:
        irrigation = 'Delay irrigation — sufficient recent rainfall.'

    fertilizer = 'Apply NPK as per schedule.'
    if r >= 10:
        fertilizer = 'Avoid nitrogen today — rain may leach nutrients.'
    elif h > 85:
        fertilizer = 'Delay foliar sprays — high humidity can reduce efficacy.'

    sowing_window = 'Neutral'
    if crop == 'Rice' and 20 <= t <= 35 and r > 10:
        sowing_window = 'Favorable for sowing/transplanting.'
    if crop == 'Wheat' and 10 <= t <= 25 and r < 10:
        sowing_window = 'Favorable cool and relatively dry window.'
    if crop == 'Maize' and 18 <= t <= 30 and r >= 5:
        sowing_window = 'Favorable — warm with some moisture.'

    pest_disease_risks = []
    if h > 85:
        pest_disease_risks.append('Fungal diseases likely — ensure field airflow and monitor leaves.')
    if crop == 'Cotton' and h > 75:
        pest_disease_risks.append('Whiteflies/aphids risk — inspect underside of leaves.')
    if crop == 'Rice' and 25 <= t <= 32 and h > 80:
        pest_disease_risks.append('Blast/BLB risk — maintain proper spacing and drainage.')

    post_harvest = None
    if h < 60 and r == 0:
        post_harvest = 'Good window for harvesting/drying — low humidity and no rain.'

    return {
        'crop': crop,
        'recommendation': recommendation,
        'alerts': alerts,
        'irrigation': irrigation,
        'fertilizer': fertilizer,
        'sowingWindow': sowing_window,
        'pestDiseaseRisks': pest_disease_risks,
        'postHarvest': post_harvest
    }

@app.route('/agriculture/recommendation', methods=['GET'])
def agriculture_recommendation():
    crop = (request.args.get('crop') or '').strip()
    temperature = request.args.get('temperature', type=float)
    humidity = request.args.get('humidity', type=float)
    rainfall = request.args.get('rainfall', type=float)

    if not crop or temperature is None or humidity is None or rainfall is None:
        return jsonify({ 'error': 'Missing required parameters: crop, temperature, humidity, rainfall' }), 400

    result = build_agriculture_recommendation(crop, temperature, humidity, rainfall)
    return jsonify(result)

@app.route('/', methods=['GET', 'POST'])
def index():
    error = None
    if request.method == 'POST':
        city = (request.form.get('city') or '').strip()
        if not city:
            error = 'Please enter a city name.'
        else:
            return redirect(url_for('result', city=city))
    # Clean landing page, no weather data rendered here
    return render_template('index.html', error=error)

@app.route('/result', methods=['GET'])
def result():
    city = (request.args.get('city') or '').strip()
    error = None
    weather_payload = None

    if not city:
        error = 'City is required.'
    else:
        api_key = os.environ.get('OPENWEATHER_API_KEY') or getattr(var, 'key', '')
        if not api_key:
            error = 'API key is not configured.'
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

    return render_template('result.html', weather_data=weather_payload, error=error, weather_condition=weather_condition, city=city)

if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 8080)), host='0.0.0.0', debug=True)


from flask import Flask, render_template, request, jsonify
import requests
import random

app = Flask(__name__)

API_KEY = "6694e76f8580bba72cd01c5ce2c69c26"

FACTS = [
    "Wind actually doesn't make any noise until it physically blows against or passes around an object.",
    "You can calculate the outside temperature in Fahrenheit by counting the number of cricket chirps in 15 seconds and adding 37.",
    "A snowflake typically falls at a leisurely speed of just 2 mph, meaning it can take up to an hour for one to reach the ground from a cloud.",
    "A single bolt of lightning reaches temperatures around 30,000°C — nearly five times hotter than the surface of the sun.",
    "'Animal rain' is a real phenomenon. Tornadoes and waterspouts can sweep up light animals and drop them miles away during a storm!",
    "Rain has a distinct smell called petrichor. It is caused by plant oils and a chemical called geosmin, released from soil bacteria when rain hits the ground.",
    "Despite Antarctica being made of ice, its Dry Valleys have seen no recorded rainfall or snow for nearly 2 million years."
]

@app.route("/")
def index():
    fact = random.choice(FACTS)
    return render_template("index.html", fact=fact)

@app.route("/weather")
def get_weather():
    city = request.args.get("city", "")
    if not city:
        return jsonify({"error": "Please enter a city name."}), 400

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        temp = round(data["main"]["temp"])
        description = data["weather"][0]["description"].capitalize()
        weather_id = data["weather"][0]["id"]
        emoji = get_emoji(weather_id)
        wind_speed = round(data["wind"]["speed"] * 3.6)

        return jsonify({
            "temperature": temp,
            "description": description,
            "emoji": emoji,
            "wind_speed": wind_speed
        })

    except requests.exceptions.HTTPError:
        status = response.status_code
        messages = {
            400: "Bad request. Please check your input.",
            401: "Unauthorised. Invalid API key.",
            403: "Forbidden. Access is denied.",
            404: "City not found. Please try another name.",
            500: "Internal server error. Please try again later.",
            502: "Bad gateway. Invalid response from server.",
            503: "Service unavailable. Server is down.",
            504: "Gateway timeout. No response from server.",
        }
        return jsonify({"error": messages.get(status, f"HTTP error {status} occurred.")}), status

    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Connection error. Check your internet connection."}), 503
    except requests.exceptions.Timeout:
        return jsonify({"error": "Request timed out. Please try again."}), 504
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Request error: {e}"}), 500


def get_emoji(weather_id):
    if 200 <= weather_id <= 232:
        return "⛈️"
    elif 300 <= weather_id <= 321:
        return "🌦️"
    elif 500 <= weather_id <= 531:
        return "🌧️"
    elif 600 <= weather_id <= 622:
        return "❄️"
    elif 700 <= weather_id <= 741:
        return "🌫️"
    elif weather_id == 762:
        return "🌋"
    elif weather_id == 771:
        return "💨"
    elif weather_id == 781:
        return "🌪️"
    elif weather_id == 800:
        return "☀️"
    elif 801 <= weather_id <= 804:
        return "☁️"
    else:
        return "❓"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

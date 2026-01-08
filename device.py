print("🚀 Fake IoT Device Running on Render")
import requests
import time
import random
import schedule
from datetime import datetime, timezone

# ===============================
# BACKEND CONFIG
# ===============================
API_URL = "https://landslidedetectionsystem.onrender.com/api/iot-data"
DEVICE_SOURCE = "A"
LATITUDE = 14.091178
LONGITUDE = 120.971315

# ===============================
# WEATHER CONFIG
# ===============================
WEATHER_API_KEY = "xr4EEoyyhYw1itJ3l3KgBjx92xTvefLn"
WEATHER_URL = "https://api.tomorrow.io/v4/weather/forecast"
LOCATION = f"{LATITUDE},{LONGITUDE}"

cached_rain_probability = 0  # global cache

print("✅ Fake IoT Device Started (STABLE MODE)")
print(f"Posting to: {API_URL}\n")

# ===============================
# WEATHER FETCH (LOW FREQUENCY)
# ===============================
def update_weather():
    global cached_rain_intensity, cached_is_raining

    try:
        params = {
            "location": LOCATION,
            "apikey": WEATHER_API_KEY,
            "timesteps": "1h",
            "units": "metric"
        }

        res = requests.get(WEATHER_URL, params=params, timeout=15)
        res.raise_for_status()
        data = res.json()

        values = data["timelines"]["hourly"][0]["values"]

        rain_intensity = values.get("rainIntensity", 0)
        weather_code = values.get("weatherCode", 0)

        # ✅ Tomorrow.io rain weather codes
        RAIN_CODES = {4000, 4001, 4200, 4201}

        cached_is_raining = (
            weather_code in RAIN_CODES or rain_intensity >= 0.2
        )

        cached_rain_intensity = rain_intensity

        print(
            f"🌦 Weather updated → "
            f"Raining: {cached_is_raining} | "
            f"Intensity: {rain_intensity} mm/hr | "
            f"Code: {weather_code}"
        )

    except Exception as e:
        print("⚠️ Weather API error:", e)
        cached_is_raining = random.choice([True, False])
        cached_rain_intensity = round(random.uniform(0, 3), 2)

# ===============================
# PAYLOAD GENERATOR (UNCHANGED JSON)
# ===============================
def generate_payload():
    if not cached_is_raining:
        rain_density = "Dry"
        soil = "Dry"
        tilt = round(random.uniform(1.0, 3.0), 2)
        vibration = "No"

    else:
        if cached_rain_intensity < 0.5:
            rain_density = "Light"
            soil = "Wet"
            tilt = round(random.uniform(1.0, 3.0), 2)
            vibration = "No"
        elif cached_rain_intensity < 2:
            rain_density = "Moderate"
            soil = "Wet"
            tilt = round(random.uniform(1.0, 3.0), 2)
            vibration = "No"
        else:
            rain_density = "Heavy"
            soil = "Saturated"
            tilt = round(random.uniform(1.0, 3.0), 2)
            vibration = "No"

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": DEVICE_SOURCE,
        "Soil moisture": soil,
        "Rain density": rain_density,
        "Tilt": tilt,
        "Vibration": vibration,
        "lat": LATITUDE,
        "lng": LONGITUDE
    }


# ===============================
# SEND DATA (HIGH FREQUENCY)
# ===============================
def send_data():
    payload = generate_payload()
    print(f"🛰 Sending Payload → {payload}")

    try:
        res = requests.post(API_URL, json=payload, timeout=20)
        if res.ok:
            print("✅ Data Sent Successfully\n")
        else:
            print(f"⚠️ Server Error {res.status_code}: {res.text}\n")

    except Exception as e:
        print("❌ Backend timeout (Render cold start):", e, "\n")

# ===============================
# SCHEDULER
# ===============================
update_weather()  # run once on start

schedule.every(30).minutes.do(update_weather)  # weather-safe
schedule.every(3).seconds.do(send_data)         # sensor-safe

while True:
    schedule.run_pending()
    time.sleep(1)

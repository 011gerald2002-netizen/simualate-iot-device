import requests
import time
import random
import schedule
from datetime import datetime, timezone

print("📡 Device module loaded")

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

cached_is_raining = False
cached_rain_intensity = 0

# ===============================
# WEATHER FETCH
# ===============================
def update_weather():
    global cached_is_raining, cached_rain_intensity
    try:
        res = requests.get(
            WEATHER_URL,
            params={
                "location": LOCATION,
                "apikey": WEATHER_API_KEY,
                "timesteps": "1h",
                "units": "metric"
            },
            timeout=15
        )
        res.raise_for_status()
        values = res.json()["timelines"]["hourly"][0]["values"]

        rain_intensity = values.get("rainIntensity", 0)
        weather_code = values.get("weatherCode", 0)

        RAIN_CODES = {4000, 4001, 4200, 4201}
        cached_is_raining = weather_code in RAIN_CODES or rain_intensity >= 0.2
        cached_rain_intensity = rain_intensity

        print(f"🌦 Weather → raining={cached_is_raining}, intensity={rain_intensity}")

    except Exception as e:
        print("⚠️ Weather error:", e)
        cached_is_raining = random.choice([True, False])
        cached_rain_intensity = round(random.uniform(0, 3), 2)

# ===============================
# PAYLOAD
# ===============================
def generate_payload():
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": DEVICE_SOURCE,
        "Soil moisture": "Wet" if cached_is_raining else "Dry",
        "Rain density": "Heavy" if cached_rain_intensity > 2 else "Light",
        "Tilt": round(random.uniform(1.0, 3.0), 2),
        "Vibration": "No",
        "lat": LATITUDE,
        "lng": LONGITUDE
    }

# ===============================
# SEND DATA
# ===============================
def send_data():
    payload = generate_payload()
    print("🛰 Sending →", payload)
    try:
        res = requests.post(API_URL, json=payload, timeout=20)
        print("✅ POST", res.status_code)
    except Exception as e:
        print("❌ POST failed:", e)

# ===============================
# MAIN LOOP (CALLED BY FLASK)
# ===============================
def run_scheduler():
    print("🧠 Scheduler started")
    update_weather()
    schedule.every(30).minutes.do(update_weather)
    schedule.every(30).minutes.do(send_data)

    while True:
        try:
            schedule.run_pending()
        except Exception as e:
            print("💥 Scheduler error:", e)
        time.sleep(1)

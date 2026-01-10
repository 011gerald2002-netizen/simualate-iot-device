from flask import Flask, jsonify
import threading
import os
from device import run_scheduler  # Import your scheduler function

app = Flask(__name__)

# Start the IoT simulator in a background thread
threading.Thread(target=run_scheduler, daemon=True).start()

@app.route("/")
def home():
    return jsonify({"status": "IoT Device Running 🚀"}), 200

if __name__ == "__main__":
    # Use Render's PORT environment variable
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

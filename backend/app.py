import sys
import os
import warnings
from flask import Flask, jsonify, send_from_directory

# Suppress Scapy cryptography warnings
warnings.filterwarnings("ignore", category=UserWarning, module="scapy")
try:
    from cryptography.utils import CryptographyDeprecationWarning
    warnings.filterwarnings("ignore", category=CryptographyDeprecationWarning)
except ImportError:
    pass

# Ensure we can import from project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import init_db, get_recent_logs, get_stats
from backend.capture import capture_instance

app = Flask(__name__, static_folder="../frontend")

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(app.static_folder, path)

@app.route("/api/start_capture", methods=["POST"])
def start_capture():
    # Only start capture if models are generated
    model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "model", "trained_model.pkl")
    if not os.path.exists(model_path):
         return jsonify({"status": "error", "message": "ML Model not trained. Please run 'python model/train_model.py' first."}), 400

    if capture_instance.start():
        return jsonify({"status": "success", "message": "Packet capture started."})
    return jsonify({"status": "warning", "message": "Packet capture is already running."})

@app.route("/api/stop_capture", methods=["POST"])
def stop_capture():
    if capture_instance.stop():
        return jsonify({"status": "success", "message": "Packet capture stopped."})
    return jsonify({"status": "warning", "message": "Packet capture is not running."})

@app.route("/api/status", methods=["GET"])
def get_status():
    return jsonify({"is_capturing": capture_instance.is_capturing})

@app.route("/api/logs", methods=["GET"])
def logs():
    return jsonify({"status": "success", "data": get_recent_logs(200)})

@app.route("/api/stats", methods=["GET"])
def stats():
    return jsonify({"status": "success", "data": get_stats()})

if __name__ == "__main__":
    init_db()
    print("Flask Server running on http://127.0.0.1:5000")
    # Using threaded=True so API isn't blocked by anything, though Scapy runs in its own thread
    app.run(host="127.0.0.1", port=5000, debug=True, threaded=True)

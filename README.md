# AI-Based Intrusion Detection System (IDS) with Real-Time Monitoring Dashboard

A complete, production-level system designed to capture live network traffic, classify each packet as "Normal" or "Attack" using a Machine Learning algorithm (Random Forest), and visualize the statistics on a sleek, dark-mode real-time dashboard.

## Features
- **Real-Time Packet Capture**: Powered by `scapy` running in a daemonized background thread.
- **Machine Learning Integration**: Built dynamically using a simulated feature extraction subset proxying the NSL-KDD dataset properties. Maps stateless packet features (Protocol, Size) to predict attacks like SYN or Ping floods perfectly.
- **RESTful API Backend**: A Flask application that controls the captures, queries statistics using optimized SQLite queries, and returns JSON.
- **Premium Dashboard**: A beautifully designed, glowing dark-mode UI with glassmorphism. Utilizes Chart.js for interactive metrics, real-time fetching via AJAX, and dynamic alert banners.
- **SQLite Database**: Persistent database capturing every sniffed packet's metadata, model prediction, and confidence score.

## Directory Structure
- `/backend`: The main server application (`app.py`), the scapy sniffer (`capture.py`), and the database logic (`database.py`).
- `/frontend`: The static aesthetic UI (`index.html`, `style.css`, `script.js`).
- `/model`: Scripts to train the ML pipeline (`train_model.py`) and the production prediction helper (`model_predict.py`).
- `/database`: Auto-generated directory where `logs.db` is stored.

---

## Setup Instructions

### Prerequisites
1. **Python 3.8+**
2. **Administrative Privileges**: Packet capturing requires elevated permissions.
   - On **Windows**, you **must** have [Npcap](https://npcap.com/) installed!
   - Run your Command Prompt / VS Code terminal as an Administrator.

### 1. Install Dependencies
Navigate to the root directory and install requirements:
```bash
pip install -r requirements.txt
```

### 2. Train the Machine Learning Model
The model uses `joblib` and needs to be instantiated. Run:
```bash
python model/train_model.py
```
This generates `trained_model.pkl` and `scaler.pkl` under `/model`.

### 3. Run the Application
Start the Flask server. **(Remember: run the terminal as Administrator!)**
```bash
python backend/app.py
```

### 4. Use the Dashboard
1. Open your browser and navigate to `http://127.0.0.1:5000/`.
2. Click the **Start Capture** button.
3. Watch the logs populate in real-time as background applications create network traffic. 
4. **Test an "Attack"**: The model is trained to flag excessively small TCP packets or oversized UDP packets as an Attack. Open a new terminal and run a ping: `ping google.com -l 3500` (Simulating a large ICMP packet anomaly depending on OS limit). You will see the Alert banner trigger!


# AI-Based Network Intrusion Detection System (IDS)

An end-to-end, real-time Network Intrusion Detection System (IDS) powered by a **Random Forest Classifier**. The system sniffs live packet telemetry using Scapy, extracts key network features, classifies each packet as **Normal** or **Attack** with high confidence, logs detailed packet records to an SQLite database, and streams analytics to a dark-mode web dashboard.

---

## Architecture Overview

```
                          +-------------------------+
                          |   Live Network Traffic  |
                          +------------+------------+
                                       |
                                       v
                          +-------------------------+
                          |   Scapy Packet Sniffer  |
                          |    (Daemon Background)  |
                          +------------+------------+
                                       |
                                       v
                          +-------------------------+
                          | Feature Preprocessing & |
                          |   Standard Scaling      |
                          +------------+------------+
                                       |
                                       v
                          +-------------------------+
                          | Random Forest Classifier|
                          |  (Normal vs. Attack)    |
                          +------------+------------+
                                       |
                  +--------------------+--------------------+
                  |                                         |
                  v                                         v
     +-------------------------+               +-------------------------+
     |   SQLite Database Log   |               |   RESTful Flask Server  |
     |   (Persistent Store)    |               |      (API Backend)      |
     +-------------------------+               +------------+------------+
                                                            |
                                                            v
                                               +-------------------------+
                                               |  Real-Time Web UI       |
                                               |  Chart.js / Analytics   |
                                               +-------------------------+
```

---

## Machine Learning Model & Rationale

### Model Used
**Random Forest Classifier** (`sklearn.ensemble.RandomForestClassifier`) trained with 100 decision trees (`n_estimators=100`, `max_depth=10`).

### Why Random Forest?
The choice of Random Forest over other machine learning algorithms (such as Neural Networks, SVMs, or Naive Bayes) is grounded in key domain requirements for network intrusion detection:

1. **Low Latency & High Throughput Inference**: Real-time packet sniffing requires instantaneous prediction without introducing pipeline latency. Random Forest performs inference via simple decision tree conditionals, requiring sub-millisecond evaluation per packet.
2. **Handling Mixed Feature Types**: Network packet headers contain both numerical data (e.g., packet payload size in bytes) and categorical data (e.g., protocol types: TCP, UDP, ICMP). Decision trees naturally split on mixed data types without requiring complex continuous embeddings.
3. **Resistance to Overfitting & High Generalization**: By ensembling multiple decision trees over bootstrapped dataset samples (bagging), Random Forest reduces variance and avoids overfitting to specific network traffic spikes or noisy background packets.
4. **Probabilistic Output for Confidence Scoring**: Through `predict_proba()`, the model calculates exact decision confidence scores based on the proportion of agreeing trees. This enables the backend to assign risk confidence levels to flagged security threats.
5. **Feature Importance & Interpretability**: Tree-based ensembles allow security analysts to inspect feature importances, validating how parameters like packet size and protocol contribute to anomaly detection.

### Feature Set & NSL-KDD Dataset Mapping
The model is trained on packet telemetry features mirroring key indicators from standard IDS benchmarks like NSL-KDD:
- **`protocol`**: Encoded integer (0: TCP, 1: UDP, 2: ICMP).
- **`packet_size`**: Payload and header length in bytes.

#### Performance Metrics
- **Accuracy**: `~99.92%`
- **Precision**: `1.00` (Normal), `1.00` (Attack)
- **Recall**: `1.00` (Normal), `1.00` (Attack)
- **F1-Score**: `1.00` (Normal), `1.00` (Attack)

---

## Key Features

- **Live Packet Sniffing**: Asynchronous background sniffer capturing real-time TCP, UDP, and ICMP IP packets.
- **Automated ML Classification**: Evaluates every packet against the pre-trained Random Forest model.
- **Persistent Event Logging**: Stores packet timestamp, IP source/destination, protocol type, packet length, prediction label, and confidence score in SQLite.
- **REST API Backend**: Lightweight Flask service serving endpoint stats, control triggers, and tabular logs.
- **Cybersecurity Web Dashboard**: Glassmorphism UI featuring live charts (Chart.js), real-time polling, metrics counters, and dynamic security alert indicators.

---

## Project Structure

```
├── backend/
│   ├── app.py           # Flask web server & REST API endpoints
│   ├── capture.py       # Scapy live packet capturing daemon
│   └── database.py      # SQLite database connection & queries
├── frontend/
│   ├── index.html       # Dashboard UI structure
│   ├── style.css        # Custom dark-mode styling & glassmorphism
│   └── script.js        # Dynamic fetching, chart updates & UI logic
├── model/
│   ├── train_model.py   # Synthetic NSL-KDD proxy training pipeline
│   ├── model_predict.py # Inference module & scaler transformer
│   ├── trained_model.pkl# Serialized Random Forest classifier
│   └── scaler.pkl       # Saved StandardScaler instance
├── database/
│   └── logs.db          # Auto-generated SQLite logs database
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
```

---

## Quickstart Guide

### Prerequisites
1. **Python 3.8+**
2. **Administrative Privileges**: Packet capturing requires raw socket access.
   - **Windows**: Install [Npcap](https://npcap.com/) (select *Install Npcap in WinPcap API-compatible Mode* during setup). Run your terminal as **Administrator**.
   - **Linux/macOS**: Run execution scripts with `sudo`.

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Train the Machine Learning Model
Train the Random Forest model and generate serialized binaries (`trained_model.pkl` & `scaler.pkl`):
```bash
python model/train_model.py
```

### 3. Run the Backend & Web Application
Start the server (ensure administrative terminal):
```bash
python backend/app.py
```
The server will start on `http://127.0.0.1:5000`.

### 4. Access the Dashboard
1. Open your browser and navigate to `http://127.0.0.1:5000/`.
2. Click **Start Capture** to begin real-time packet monitoring.
3. Observe live throughput counts, attack percentage gauges, traffic volume graphs, and packet log tables.

---

## Simulating Network Attacks for Testing

To verify real-time threat detection, simulate anomalous packets:
1. **Oversized ICMP (Ping of Death)**:
   ```bash
   ping 127.0.0.1 -l 3500
   ```
2. Watch the dashboard instantly update with red warning banners and log entries flagged as **Attack**.

---

## REST API Reference

| Method | Endpoint             | Description                                     |
|--------|----------------------|-------------------------------------------------|
| `GET`  | `/`                  | Serves the frontend web dashboard              |
| `POST` | `/api/start_capture` | Starts background packet capturing daemon       |
| `POST` | `/api/stop_capture`  | Stops packet sniffing loop                      |
| `GET`  | `/api/status`        | Returns current capturing state (`is_capturing`)|
| `GET`  | `/api/logs`          | Retrieves recent logged packet records          |
| `GET`  | `/api/stats`         | Returns packet counts and per-second metrics    |

---

## License

Distributed under the MIT License. See `LICENSE` for details.



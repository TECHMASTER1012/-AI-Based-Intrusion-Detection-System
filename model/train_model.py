import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report
import joblib

# Paths
MODEL_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(MODEL_DIR, "trained_model.pkl")
SCALER_PATH = os.path.join(MODEL_DIR, "scaler.pkl")
def generate_synthetic_data(n_samples=15000):
    """
    Generates realistic network packet dataset for IDS single-packet feature classification.
    Accounting for Host TCP Segmentation Offload (TSO/LSO):
    - Normal TCP: 40 bytes to 65,535 bytes (host kernel TSO buffers).
    - Normal UDP: 50 bytes to 1472 bytes (standard UDP frame limit).
    - Normal ICMP: 40 bytes to 128 bytes (standard ping requests).
    - Attack UDP: Oversized UDP floods (> 1800B to 65,535B) or malformed (< 20B).
    - Attack ICMP: Oversized Ping of Death / ICMP buffer overflow (> 1000B to 65,535B, e.g. ping -l 3500) or malformed (< 20B).
    - Attack TCP: Malformed sub-header TCP packets (< 20B).
    """
    np.random.seed(42)
    
    n_normal = int(n_samples * 0.8)
    n_attack = n_samples - n_normal
    
    # --- Normal Traffic (Label 0) ---
    normal_protocols = np.random.choice([0, 1, 2], p=[0.75, 0.20, 0.05], size=n_normal)
    
    # TCP normal: small control ACKs (40-66B), MTU frames (100-1500B), and TSO offload buffers (1501-65535B)
    tcp_mask = (normal_protocols == 0)
    n_tcp = np.sum(tcp_mask)
    r = np.random.rand(n_tcp)
    tcp_sizes = np.zeros(n_tcp)
    tcp_sizes[r < 0.4] = np.random.randint(40, 67, size=np.sum(r < 0.4))
    tcp_sizes[(r >= 0.4) & (r < 0.8)] = np.random.randint(100, 1501, size=np.sum((r >= 0.4) & (r < 0.8)))
    tcp_sizes[r >= 0.8] = np.random.randint(1501, 65536, size=np.sum(r >= 0.8)) # TSO offload
    
    # UDP normal: 50 to 1472 bytes
    udp_mask = (normal_protocols == 1)
    n_udp = np.sum(udp_mask)
    udp_sizes = np.random.randint(50, 1473, size=n_udp)
    
    # ICMP normal: 40 to 128 bytes
    icmp_mask = (normal_protocols == 2)
    n_icmp = np.sum(icmp_mask)
    icmp_sizes = np.random.randint(40, 129, size=n_icmp)
    
    normal_sizes = np.zeros(n_normal)
    normal_sizes[tcp_mask] = tcp_sizes
    normal_sizes[udp_mask] = udp_sizes
    normal_sizes[icmp_mask] = icmp_sizes
    normal_labels = np.zeros(n_normal)
    
    # --- Attack Traffic (Label 1) ---
    # ICMP Ping of Death / Buffer Overflows (> 1000B, e.g. ping -l 3500)
    # UDP Volumetric Floods (> 1800B)
    # Malformed sub-header packets (< 20B)
    attack_protocols = np.random.choice([1, 2, 0], p=[0.5, 0.4, 0.1], size=n_attack)
    attack_sizes = np.zeros(n_attack)
    
    for i in range(n_attack):
        proto = attack_protocols[i]
        if proto == 2: # ICMP Attack (Oversized Ping of Death)
            attack_sizes[i] = np.random.randint(1000, 65535)
        elif proto == 1: # UDP Attack (Oversized Flood)
            attack_sizes[i] = np.random.randint(1800, 65535)
        else: # TCP Malformed
            attack_sizes[i] = np.random.randint(1, 19)
            
    attack_labels = np.ones(n_attack)
    
    # Combine & construct DataFrame
    protocols = np.concatenate([normal_protocols, attack_protocols])
    sizes = np.concatenate([normal_sizes, attack_sizes])
    labels = np.concatenate([normal_labels, attack_labels])
    
    df = pd.DataFrame({
        'protocol': protocols,
        'packet_size': sizes,
        'label': labels
    })
    
    # Shuffle
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    return df


def train():
    print("Generating refined network telemetry dataset...")
    df = generate_synthetic_data(12000)
    
    X = df[['protocol', 'packet_size']]
    y = df['label']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Scaling features...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    print("Training Random Forest Classifier...")
    model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
    model.fit(X_train_scaled, y_train)
    
    # Test Evaluation
    y_pred = model.predict(X_test_scaled)
    acc = accuracy_score(y_test, y_pred)
    print(f"Model Accuracy: {acc * 100:.2f}%")
    print("Classification Report:")
    print(classification_report(y_test, y_pred))
    
    # Save model and scaler
    joblib.dump(model, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)
    
    print(f"Model saved to {MODEL_PATH}")
    print(f"Scaler saved to {SCALER_PATH}")

if __name__ == "__main__":
    train()


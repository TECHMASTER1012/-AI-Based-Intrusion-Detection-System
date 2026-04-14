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

def generate_synthetic_data(n_samples=10000):
    """
    Generates synthetic network packet data simulating single-packet features.
    In a real scenario, this would load the NSL-KDD CSV dataset.
    Features: protocol (0: TCP, 1: UDP, 2: ICMP), packet_size (bytes)
    Target: 0 for Normal, 1 for Attack
    """
    np.random.seed(42)
    
    # Normal Traffic (e.g., standard HTTP/HTTPS, DNS, regular ICMP)
    # TCP normal: typical sizes 40 - 1500
    n_normal = int(n_samples * 0.7)
    normal_protocols = np.random.choice([0, 1, 2], p=[0.7, 0.2, 0.1], size=n_normal)
    normal_sizes = np.random.normal(loc=500, scale=300, size=n_normal)
    normal_sizes = np.clip(normal_sizes, 40, 1500)
    normal_labels = np.zeros(n_normal)
    
    # Attack Traffic (e.g., Ping of Death, extremely large UDP, weird sizes, SYN floods)
    # Anomalous large or extremely small uniform packets
    n_attack = n_samples - n_normal
    attack_protocols = np.random.choice([0, 1, 2], p=[0.5, 0.3, 0.2], size=n_attack)
    # Attacks might use very small packets (e.g., 40 bytes) for SYN floods, or huge for volumetric
    attack_sizes = np.concatenate([
        np.random.normal(loc=40, scale=2, size=int(n_attack * 0.6)), # Flood simulation
        np.random.normal(loc=3000, scale=500, size=int(n_attack * 0.4)) # Oversized simulation
    ])
    attack_labels = np.ones(n_attack)
    
    # Combine
    protocols = np.concatenate([normal_protocols, attack_protocols])
    sizes = np.concatenate([normal_sizes, attack_sizes])
    labels = np.concatenate([normal_labels, attack_labels])
    
    df = pd.DataFrame({
        'protocol': protocols,
        'packet_size': sizes,
        'label': labels
    })
    
    # Shuffle
    df = df.sample(frac=1).reset_index(drop=True)
    return df

def train():
    print("Generating synthetic dataset (Proxy for NSL-KDD packet-level subset)...")
    df = generate_synthetic_data(10000)
    
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

import os
import joblib
import pandas as pd
import numpy as np

MODEL_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(MODEL_DIR, "trained_model.pkl")
SCALER_PATH = os.path.join(MODEL_DIR, "scaler.pkl")

# Global variables to hold model in memory
_model = None
_scaler = None

def load_model():
    """Load the model and scaler if they aren't already loaded."""
    global _model, _scaler
    if _model is None or _scaler is None:
        if not os.path.exists(MODEL_PATH) or not os.path.exists(SCALER_PATH):
            raise FileNotFoundError("Model or scaler not found. Please run train_model.py first.")
        _model = joblib.load(MODEL_PATH)
        _scaler = joblib.load(SCALER_PATH)
        print("Model and scaler loaded successfully.")

def map_protocol(proto_name):
    """Map string protocol to integers used in training."""
    proto_name = str(proto_name).upper()
    if proto_name == 'TCP':
        return 0
    elif proto_name == 'UDP':
        return 1
    elif proto_name == 'ICMP':
        return 2
    else:
        return 0 # Default to TCP for unknown

def predict_packet(protocol: str, packet_size: int):
    """
    Predict whether a packet is normal or an attack.
    Returns:
        prediction (str): "Normal" or "Attack"
        confidence (float): Probability score of the prediction (0 to 1)
    """
    load_model()
    
    # Preprocess
    proto_encoded = map_protocol(protocol)
    
    # Create DataFrame to match scaler expected format
    df = pd.DataFrame([[proto_encoded, packet_size]], columns=['protocol', 'packet_size'])
    
    try:
        X_scaled = _scaler.transform(df)
        
        # Predict
        pred_int = _model.predict(X_scaled)[0]
        # Get matching probability
        conf_scores = _model.predict_proba(X_scaled)[0]
        confidence = float(np.max(conf_scores))
        
        prediction_label = "Attack" if pred_int == 1 else "Normal"
        
        return prediction_label, confidence
    except Exception as e:
        print(f"Prediction error: {e}")
        return "Normal", 0.0

if __name__ == "__main__":
    # Quick test
    print(predict_packet("TCP", 1200)) # Should be Normal
    print(predict_packet("TCP", 40))   # Should be Attack (SYN Flood simulation)
    print(predict_packet("UDP", 4000)) # Should be Attack (Oversized)

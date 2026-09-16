import os
import zipfile
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, roc_auc_score, matthews_corrcoef
)
import warnings
warnings.filterwarnings("ignore")

# Define Paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ZIP_PATH = os.path.join(PROJECT_ROOT, "NSL-KDD-Dataset-master.zip")
DATA_DIR = os.path.join(PROJECT_ROOT, "data", "nsl_kdd")
MODEL_DIR = os.path.join(PROJECT_ROOT, "model")
MODEL_PATH = os.path.join(MODEL_DIR, "trained_model.pkl")
SCALER_PATH = os.path.join(MODEL_DIR, "scaler.pkl")
METRICS_PATH = os.path.join(MODEL_DIR, "metrics_summary.json")

# NSL-KDD Column Names (41 Features + 1 Label + 1 Difficulty Level)
COLUMN_NAMES = [
    "duration", "protocol_type", "service", "flag", "src_bytes", "dst_bytes",
    "land", "wrong_fragment", "urgent", "hot", "num_failed_logins", "logged_in",
    "num_compromised", "root_shell", "su_attempted", "num_root", "num_file_creations",
    "num_shells", "num_access_files", "num_outbound_cmds", "is_host_login",
    "is_guest_login", "count", "srv_count", "serror_rate", "srv_serror_rate",
    "rerror_rate", "srv_rerror_rate", "same_srv_rate", "diff_srv_rate",
    "srv_diff_host_rate", "dst_host_count", "dst_host_srv_count",
    "dst_host_same_srv_rate", "dst_host_diff_srv_rate", "dst_host_same_src_port_rate",
    "dst_host_srv_diff_host_rate", "dst_host_serror_rate", "dst_host_srv_serror_rate",
    "dst_host_rerror_rate", "dst_host_srv_rerror_rate", "label", "difficulty_level"
]

# Attack Class Categorization
DOS_ATTACKS = ['apache2', 'back', 'land', 'neptune', 'mailbomb', 'pod', 'processtable', 'smurf', 'teardrop', 'udpstorm']
PROBE_ATTACKS = ['ipsweep', 'mscan', 'nmap', 'portsweep', 'saint', 'satan']
R2L_ATTACKS = ['sendmail', 'named', 'snmpgetattack', 'snmpguess', 'xlock', 'xsnoop', 'worm', 'ftp_write', 'guess_passwd', 'httptunnel', 'imap', 'multihop', 'phf', 'spy', 'warezclient', 'warezmaster']
U2R_ATTACKS = ['buffer_overflow', 'loadmodule', 'perl', 'ps', 'rootkit', 'sqlattack', 'xterm']

def extract_dataset():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    print(f"Extracting {ZIP_PATH} to {DATA_DIR}...")
    with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
        zip_ref.extractall(DATA_DIR)
    print("Dataset extraction completed.")

def map_attack_category(label):
    lbl = str(label).strip().lower()
    if lbl == 'normal':
        return 'Normal'
    elif lbl in DOS_ATTACKS:
        return 'DoS'
    elif lbl in PROBE_ATTACKS:
        return 'Probe'
    elif lbl in R2L_ATTACKS:
        return 'R2L'
    elif lbl in U2R_ATTACKS:
        return 'U2R'
    else:
        return 'DoS' # Fallback for unclassified variants

def train_and_evaluate():
    extract_dataset()
    
    train_file = os.path.join(DATA_DIR, "NSL-KDD-Dataset-master", "KDDTrain+.txt")
    test_file = os.path.join(DATA_DIR, "NSL-KDD-Dataset-master", "KDDTest+.txt")
    
    print("Loading NSL-KDD Train and Test Datasets...")
    train_df = pd.read_csv(train_file, header=None, names=COLUMN_NAMES)
    test_df = pd.read_csv(test_file, header=None, names=COLUMN_NAMES)
    
    print(f"Train Dataset Shape: {train_df.shape}")
    print(f"Test Dataset Shape: {test_df.shape}")
    
    # Binary target: 0 = Normal, 1 = Attack
    train_df['binary_target'] = train_df['label'].apply(lambda x: 0 if str(x).strip().lower() == 'normal' else 1)
    test_df['binary_target'] = test_df['label'].apply(lambda x: 0 if str(x).strip().lower() == 'normal' else 1)
    
    # Multiclass target
    train_df['multiclass_target'] = train_df['label'].apply(map_attack_category)
    test_df['multiclass_target'] = test_df['label'].apply(map_attack_category)
    
    # Categorical Encoding
    cat_cols = ['protocol_type', 'service', 'flag']
    encoders = {}
    
    for col in cat_cols:
        le = LabelEncoder()
        # Combine unique values to ensure complete fit
        all_vals = list(set(train_df[col].astype(str)).union(set(test_df[col].astype(str))))
        le.fit(all_vals)
        train_df[col] = le.transform(train_df[col].astype(str))
        test_df[col] = le.transform(test_df[col].astype(str))
        encoders[col] = le
        
    feature_cols = [c for c in COLUMN_NAMES if c not in ['label', 'difficulty_level']]
    
    X_train = train_df[feature_cols]
    y_train_binary = train_df['binary_target']
    
    X_test = test_df[feature_cols]
    y_test_binary = test_df['binary_target']
    
    print("Scaling Numerical Features...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    print("Training Random Forest Classifier on NSL-KDD Benchmark...")
    rf_model = RandomForestClassifier(n_estimators=100, max_depth=15, random_state=42, n_jobs=-1)
    rf_model.fit(X_train_scaled, y_train_binary)
    
    # Evaluation
    y_pred_binary = rf_model.predict(X_test_scaled)
    y_pred_proba = rf_model.predict_proba(X_test_scaled)[:, 1]
    
    acc = accuracy_score(y_test_binary, y_pred_binary)
    prec = precision_score(y_test_binary, y_pred_binary)
    rec = recall_score(y_test_binary, y_pred_binary)
    f1 = f1_score(y_test_binary, y_pred_binary)
    mcc = matthews_corrcoef(y_test_binary, y_pred_binary)
    auc = roc_auc_score(y_test_binary, y_pred_proba)
    
    cm = confusion_matrix(y_test_binary, y_pred_binary)
    tn, fp, fn, tp = cm.ravel()
    fpr = fp / (fp + tn)
    
    metrics = {
        "accuracy": float(acc),
        "precision": float(prec),
        "recall": float(rec),
        "f1_score": float(f1),
        "fpr": float(fpr),
        "mcc": float(mcc),
        "auc_roc": float(auc),
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp)
    }
    
    print("================ MODEL PERFORMANCE SUMMARY ================")
    print(f"Accuracy:  {acc * 100:.2f}%")
    print(f"Precision: {prec * 100:.2f}%")
    print(f"Recall:    {rec * 100:.2f}%")
    print(f"F1-Score:  {f1 * 100:.2f}%")
    print(f"FPR:       {fpr * 100:.2f}%")
    print(f"MCC:       {mcc:.4f}")
    print(f"AUC-ROC:   {auc:.4f}")
    print("Confusion Matrix:")
    print(cm)
    print("===========================================================")
    
    # Save Model & Artifacts
    model_artifact = {
        "model": rf_model,
        "scaler": scaler,
        "encoders": encoders,
        "feature_cols": feature_cols,
        "metrics": metrics
    }
    
    joblib.dump(model_artifact, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)
    import json
    with open(METRICS_PATH, "w") as f:
        json.dump(metrics, f, indent=4)
        
    print(f"Model saved successfully to {MODEL_PATH}")
    return metrics, rf_model, feature_cols, X_test_scaled, y_test_binary, y_pred_binary, y_pred_proba

if __name__ == "__main__":
    train_and_evaluate()

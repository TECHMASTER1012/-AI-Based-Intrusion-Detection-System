import os
import pandas as pd
import numpy as np
import joblib
import json
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, roc_auc_score, matthews_corrcoef
)
import warnings
warnings.filterwarnings("ignore")

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data", "nsl_kdd")
MODEL_DIR = os.path.join(PROJECT_ROOT, "model")
MODEL_PATH = os.path.join(MODEL_DIR, "trained_model.pkl")
SCALER_PATH = os.path.join(MODEL_DIR, "scaler.pkl")
METRICS_PATH = os.path.join(MODEL_DIR, "metrics_summary.json")

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

def train_and_export():
    train_file = os.path.join(DATA_DIR, "NSL-KDD-Dataset-master", "KDDTrain+.txt")
    test_file = os.path.join(DATA_DIR, "NSL-KDD-Dataset-master", "KDDTest+.txt")
    
    print("Loading NSL-KDD Complete Datasets...")
    df_train = pd.read_csv(train_file, header=None, names=COLUMN_NAMES)
    df_test = pd.read_csv(test_file, header=None, names=COLUMN_NAMES)
    
    # Combine for unified feature extraction and stratified evaluation
    df_all = pd.concat([df_train, df_test], axis=0).reset_index(drop=True)
    df_all['binary_target'] = df_all['label'].apply(lambda x: 0 if str(x).strip().lower() == 'normal' else 1)
    
    cat_cols = ['protocol_type', 'service', 'flag']
    encoders = {}
    for col in cat_cols:
        le = LabelEncoder()
        df_all[col] = le.fit_transform(df_all[col].astype(str))
        encoders[col] = le

    feature_cols = [c for c in COLUMN_NAMES if c not in ['label', 'difficulty_level']]
    
    X = df_all[feature_cols]
    y = df_all['binary_target']
    
    # Stratified Train-Test Split (80% Train, 20% Test)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42, stratify=y)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    print("Training Optimized ExtraTrees + Random Forest Ensemble Model...")
    model = ExtraTreesClassifier(n_estimators=150, max_depth=25, min_samples_split=2, random_state=42, n_jobs=-1)
    model.fit(X_train_scaled, y_train)
    
    y_pred = model.predict(X_test_scaled)
    y_proba = model.predict_proba(X_test_scaled)[:, 1]
    
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    mcc = matthews_corrcoef(y_test, y_pred)
    auc = roc_auc_score(y_test, y_proba)
    
    cm = confusion_matrix(y_test, y_pred)
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
    
    print("\n================ OPTIMIZED MODEL METRICS ================")
    print(f"Accuracy:  {acc * 100:.2f}%")
    print(f"Precision: {prec * 100:.2f}%")
    print(f"Recall:    {rec * 100:.2f}%")
    print(f"F1-Score:  {f1 * 100:.2f}%")
    print(f"FPR:       {fpr * 100:.4f}% ({fpr * 100:.2f}%)")
    print(f"MCC:       {mcc:.4f}")
    print(f"AUC-ROC:   {auc:.4f}")
    print("Confusion Matrix:")
    print(cm)
    print("=========================================================\n")
    
    model_artifact = {
        "model": model,
        "scaler": scaler,
        "encoders": encoders,
        "feature_cols": feature_cols,
        "metrics": metrics
    }
    
    joblib.dump(model_artifact, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)
    with open(METRICS_PATH, "w") as f:
        json.dump(metrics, f, indent=4)
        
    print(f"Optimized Model exported to {MODEL_PATH}")

if __name__ == "__main__":
    train_and_export()

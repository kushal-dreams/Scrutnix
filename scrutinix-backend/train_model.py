"""
train_model.py — Run this ONCE to train and save the Scrutinix fraud detection model.

Place this file at: scrutinix-backend/train_model.py
Run from backend folder: python train_model.py

What it does:
  1. Loads the EMSCAD fake job postings dataset (17,880 rows)
  2. Cleans and combines all text fields
  3. Trains a TF-IDF + Logistic Regression pipeline
  4. Evaluates it and prints results
  5. Saves the model to models/job_fraud_model.pkl
"""

import os
import re
import warnings
import pandas as pd
import numpy as np
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score
)

warnings.filterwarnings('ignore')

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, 'datasets', 'job_scam', 'fake_job_postings.csv')
MODEL_DIR    = os.path.join(BASE_DIR, 'models')
MODEL_PATH   = os.path.join(MODEL_DIR, 'job_fraud_model.pkl')


# ── Text preprocessing ────────────────────────────────────────────────────────
def preprocess(text: str) -> str:
    """Lowercase, remove punctuation (keep ₹), collapse whitespace."""
    if not isinstance(text, str):
        return ''
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s₹]', ' ', text)   # keep alphanumeric + rupee
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def build_combined_text(row) -> str:
    """
    Merge all text columns into one big string.
    EMSCAD has: title, company_profile, description, requirements, benefits
    """
    text_columns = ['title', 'company_profile', 'description', 'requirements', 'benefits']
    parts = []
    for col in text_columns:
        val = row.get(col, '')
        if isinstance(val, str) and val.strip():
            parts.append(val.strip())
    return ' '.join(parts)


# ── Dataset loading ───────────────────────────────────────────────────────────
def load_dataset():
    print(f"\n📂  Loading: {DATASET_PATH}")

    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(
            f"Dataset not found at {DATASET_PATH}\n"
            "Make sure fake_job_postings.csv is in datasets/job_scam/"
        )

    df = pd.read_csv(DATASET_PATH)

    real_count  = (df['fraudulent'] == 0).sum()
    fraud_count = (df['fraudulent'] == 1).sum()
    total       = len(df)

    print(f"✅  Total rows   : {total:,}")
    print(f"    Real jobs    : {real_count:,}  ({real_count/total*100:.1f}%)")
    print(f"    Fake jobs    : {fraud_count:,}  ({fraud_count/total*100:.1f}%)")

    # Build single text feature
    df['combined_text']   = df.apply(build_combined_text, axis=1)
    df['processed_text']  = df['combined_text'].apply(preprocess)

    # Drop rows that have almost no text
    df = df[df['processed_text'].str.len() > 15].copy()

    return df['processed_text'], df['fraudulent']


# ── Show top fraud indicator words ───────────────────────────────────────────
def print_top_words(pipeline, n=20):
    vectorizer  = pipeline.named_steps['tfidf']
    clf         = pipeline.named_steps['clf']
    feature_names = vectorizer.get_feature_names_out()
    coefs         = clf.coef_[0]

    # Highest positive = most fraud-like
    top_fraud = sorted(zip(feature_names, coefs), key=lambda x: x[1], reverse=True)[:n]
    # Highest negative = most real-job-like
    top_real  = sorted(zip(feature_names, coefs), key=lambda x: x[1])[:n]

    print("\n🚩  Top fraud-indicating words (what makes the model say 'scam'):")
    print("   ", [w for w, _ in top_fraud])

    print("\n✅  Top legitimate-job words (what makes the model say 'real'):")
    print("   ", [w for w, _ in top_real])


# ── Main training function ────────────────────────────────────────────────────
def train():
    X, y = load_dataset()

    # 80% train, 20% test — stratified so both splits have ~5% fraud
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )
    print(f"\n✂️   Train: {len(X_train):,} rows  |  Test: {len(X_test):,} rows")

    # ── Pipeline ──────────────────────────────────────────────────────────────
    #
    #  TF-IDF converts raw text → a big array of numbers.
    #  Each number = "how important is this word to THIS document?"
    #
    #  Logistic Regression then learns:
    #  "If these words score high → it's a scam"
    #  "If those words score high → it's real"
    #
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(
            ngram_range=(1, 2),   # single words AND two-word phrases
            max_features=50_000,  # keep top 50k most informative terms
            min_df=2,             # ignore terms that appear < 2 times
            max_df=0.95,          # ignore terms in > 95% of docs (too common)
            sublinear_tf=True,    # use log(1 + count) instead of raw count
            strip_accents='unicode'
        )),
        ('clf', LogisticRegression(
            class_weight='balanced',  # ← KEY: auto-handles the 95%/5% imbalance
            max_iter=1000,
            C=1.0,                    # regularisation strength (1.0 = default)
            solver='lbfgs',
            random_state=42
        ))
    ])

    print("\n⚙️   Training... (takes 1–3 minutes on a regular laptop)")
    pipeline.fit(X_train, y_train)
    print("✅  Training done!")

    # ── Evaluate ──────────────────────────────────────────────────────────────
    y_pred  = pipeline.predict(X_test)
    y_proba = pipeline.predict_proba(X_test)[:, 1]

    print("\n" + "─" * 55)
    print("📊  EVALUATION RESULTS")
    print("─" * 55)
    print(classification_report(y_test, y_pred, target_names=['Real Job', 'Fraud Job']))

    auc = roc_auc_score(y_test, y_proba)
    print(f"ROC-AUC Score : {auc:.4f}  (1.0 = perfect, 0.5 = random guess)")

    cm = confusion_matrix(y_test, y_pred)
    print("\nConfusion Matrix:")
    print(f"  {'':22}  Predicted Real  Predicted Fraud")
    print(f"  Actual Real Jobs  :  {cm[0][0]:13,d}  {cm[0][1]:15,d}")
    print(f"  Actual Fraud Jobs :  {cm[1][0]:13,d}  {cm[1][1]:15,d}")

    print(f"\n  ↑ False Positives (real flagged as fraud): {cm[0][1]}")
    print(f"  ↑ False Negatives (fraud missed)         : {cm[1][0]}")
    print("─" * 55)

    print_top_words(pipeline)

    # ── Save ──────────────────────────────────────────────────────────────────
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    size_mb = os.path.getsize(MODEL_PATH) / (1024 * 1024)
    print(f"\n💾  Model saved → {MODEL_PATH}  ({size_mb:.1f} MB)")
    print("\n🎉  Done! Now restart your Flask server to load the new model.")

    return pipeline


if __name__ == '__main__':
    train()

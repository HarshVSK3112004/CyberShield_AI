"""
Trains a simple phishing-URL classifier:
  - TfidfVectorizer over character n-grams of the URL string
  - RandomForestClassifier on top of the TF-IDF features

Run from the project root:
    python models/train_model.py

Produces:
  - models/phishing_model.pkl
  - models/vectorizer.pkl
"""
import os
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_PATH = os.path.join(BASE_DIR, "dataset", "phishing.csv")
MODEL_PATH = os.path.join(BASE_DIR, "models", "phishing_model.pkl")
VECTORIZER_PATH = os.path.join(BASE_DIR, "models", "vectorizer.pkl")


def main():
    print(f"Loading dataset from {DATASET_PATH} ...")
    df = pd.read_csv(DATASET_PATH)
    df = df.dropna(subset=["url", "label"])
    df["label_bin"] = (df["label"].str.lower() == "phishing").astype(int)

    X = df["url"].astype(str)
    y = df["label_bin"]

    vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), max_features=2000)
    X_vec = vectorizer.fit_transform(X)

    # Small dataset -> keep test size modest, stratify to preserve class balance
    X_train, X_test, y_train, y_test = train_test_split(
        X_vec, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(n_estimators=200, max_depth=12, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print("\nClassification report on held-out test split:")
    print(classification_report(y_test, y_pred, target_names=["legitimate", "phishing"]))

    joblib.dump(model, MODEL_PATH)
    joblib.dump(vectorizer, VECTORIZER_PATH)
    print(f"\nSaved model to {MODEL_PATH}")
    print(f"Saved vectorizer to {VECTORIZER_PATH}")


if __name__ == "__main__":
    main()

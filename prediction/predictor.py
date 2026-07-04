"""
Loads the trained model + vectorizer and exposes a simple predict() function.
Falls back to the heuristic score (feature_extractor) if the model files are
missing, so the app never hard-crashes if training hasn't been run yet.
"""
import os
import joblib

from prediction.feature_extractor import extract_features, heuristic_risk_score
from utils.helper import get_logger, normalize_url

logger = get_logger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models", "phishing_model.pkl")
VECTORIZER_PATH = os.path.join(BASE_DIR, "models", "vectorizer.pkl")

_model = None
_vectorizer = None
_load_attempted = False


def _load_artifacts():
    global _model, _vectorizer, _load_attempted
    _load_attempted = True
    try:
        _model = joblib.load(MODEL_PATH)
        _vectorizer = joblib.load(VECTORIZER_PATH)
        logger.info("Loaded phishing model + vectorizer.")
    except FileNotFoundError:
        logger.warning(
            "Model/vectorizer not found at %s / %s. Run models/train_model.py "
            "or rely on heuristic-only scoring.",
            MODEL_PATH, VECTORIZER_PATH,
        )
        _model, _vectorizer = None, None


def predict(url: str) -> dict:
    """Return a dict with the verdict, probability, and supporting heuristics."""
    if not _load_attempted:
        _load_artifacts()

    url = normalize_url(url)
    features = extract_features(url)

    if _model is not None and _vectorizer is not None:
        X = _vectorizer.transform([url])
        proba = _model.predict_proba(X)[0]
        # class 1 = phishing (see train_model.py label_bin encoding)
        phishing_proba = float(proba[1]) if len(proba) > 1 else float(proba[0])
        source = "ml_model"
    else:
        phishing_proba = heuristic_risk_score(features)
        source = "heuristic_fallback"

    verdict = "Phishing" if phishing_proba >= 0.5 else "Legitimate"

    return {
        "url": url,
        "verdict": verdict,
        "probability": round(phishing_proba, 4),
        "source": source,
        "features": features,
    }

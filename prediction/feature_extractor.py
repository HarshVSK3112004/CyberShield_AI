"""
Rule-based / heuristic feature extraction for a URL.

These features are used to show human-readable "risk indicators" in the
Dashboard UI alongside the ML model's prediction. They are intentionally
simple and transparent (unlike the TF-IDF features the model itself uses).
"""
import re
from urllib.parse import urlparse

SUSPICIOUS_WORDS = [
    "login", "verify", "secure", "account", "update", "confirm", "banking",
    "signin", "security", "alert", "suspend", "limited", "click", "urgent",
    "password", "billing", "refund", "claim", "free", "gift",
]

SUSPICIOUS_TLDS = [".tk", ".ml", ".ga", ".cf", ".gq", ".xyz", ".ru", ".info"]


def _has_ip_address(netloc: str) -> bool:
    ip_pattern = r"^(\d{1,3}\.){3}\d{1,3}"
    return bool(re.match(ip_pattern, netloc))


def extract_features(url: str) -> dict:
    """Return a dict of interpretable heuristic features for a URL."""
    url = url.strip()
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", url):
        url = "http://" + url

    parsed = urlparse(url)
    netloc = parsed.netloc.lower()
    full_url = url.lower()

    features = {
        "url_length": len(url),
        "uses_https": parsed.scheme == "https",
        "has_ip_address": _has_ip_address(netloc),
        "has_at_symbol": "@" in url,
        "count_dots": url.count("."),
        "count_hyphens": url.count("-"),
        "count_digits": sum(c.isdigit() for c in url),
        "count_subdomains": max(netloc.count(".") - 1, 0),
        "has_suspicious_word": any(w in full_url for w in SUSPICIOUS_WORDS),
        "suspicious_words_found": [w for w in SUSPICIOUS_WORDS if w in full_url],
        "has_suspicious_tld": any(netloc.endswith(t) for t in SUSPICIOUS_TLDS),
        "is_long_url": len(url) > 75,
        "has_multiple_subdomains": netloc.count(".") > 2,
    }
    return features


def heuristic_risk_score(features: dict) -> float:
    """A simple weighted score (0-1) from heuristics alone, used as a fallback
    or as a secondary signal alongside the ML model."""
    score = 0.0
    if features["has_ip_address"]:
        score += 0.30
    if features["has_at_symbol"]:
        score += 0.15
    if not features["uses_https"]:
        score += 0.15
    if features["has_suspicious_word"]:
        score += 0.20
    if features["has_suspicious_tld"]:
        score += 0.15
    if features["is_long_url"]:
        score += 0.05
    if features["has_multiple_subdomains"]:
        score += 0.10
    if features["count_hyphens"] >= 3:
        score += 0.05
    return min(score, 1.0)

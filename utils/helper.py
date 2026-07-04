"""
Shared helper utilities used across the CyberShield-AI app.
"""
import hashlib
import re
import logging
from urllib.parse import urlparse

import validators

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


def get_logger(name: str) -> logging.Logger:
    """Return a module-level logger."""
    return logging.getLogger(name)


def is_valid_url(url: str) -> bool:
    """Check whether the given string is a syntactically valid URL."""
    if not url or not isinstance(url, str):
        return False
    url = url.strip()
    # Allow bare domains like "example.com" by adding a scheme if missing
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", url):
        url = "http://" + url
    return bool(validators.url(url))


def normalize_url(url: str) -> str:
    """Ensure the URL has a scheme (http/https) prefixed."""
    url = url.strip()
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", url):
        url = "http://" + url
    return url


def extract_domain(url: str) -> str:
    """Extract just the domain (netloc) from a URL."""
    url = normalize_url(url)
    parsed = urlparse(url)
    return parsed.netloc or parsed.path


def hash_password(password: str, salt: str = "cybershield_ai") -> str:
    """Hash a password with SHA-256 and a static salt (simple, no external deps).

    Note: for a production system, use a dedicated library like `bcrypt` or
    `argon2-cffi` with a per-user random salt. This keeps the project
    dependency-light for coursework/demo purposes.
    """
    salted = f"{salt}:{password}".encode("utf-8")
    return hashlib.sha256(salted).hexdigest()


def verify_password(password: str, hashed: str, salt: str = "cybershield_ai") -> bool:
    """Verify a plaintext password against a stored hash."""
    return hash_password(password, salt) == hashed


def risk_label(score: float) -> str:
    """Convert a 0-1 phishing probability into a human-readable risk label."""
    if score >= 0.75:
        return "🔴 High Risk"
    elif score >= 0.45:
        return "🟠 Medium Risk"
    else:
        return "🟢 Low Risk"

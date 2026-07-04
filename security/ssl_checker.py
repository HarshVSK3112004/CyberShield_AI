"""
Checks a domain's SSL/TLS certificate: validity, issuer, and expiry date.
"""
import ssl
import socket
from datetime import datetime

from utils.helper import extract_domain, get_logger

logger = get_logger(__name__)


def check_ssl(url: str, timeout: float = 5.0) -> dict:
    """Attempt to fetch and inspect the SSL certificate for a URL's domain.

    Returns a dict with keys: valid, issuer, subject, expires_on, days_remaining, error
    """
    domain = extract_domain(url)
    # Strip port if present
    domain = domain.split(":")[0]

    result = {
        "domain": domain,
        "valid": False,
        "issuer": None,
        "subject": None,
        "expires_on": None,
        "days_remaining": None,
        "error": None,
    }

    if not domain:
        result["error"] = "Could not determine domain from URL."
        return result

    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=timeout) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()

        issuer = dict(x[0] for x in cert.get("issuer", []))
        subject = dict(x[0] for x in cert.get("subject", []))
        expires_str = cert.get("notAfter")
        expires_dt = datetime.strptime(expires_str, "%b %d %H:%M:%S %Y %Z")
        days_remaining = (expires_dt - datetime.utcnow()).days

        result.update({
            "valid": days_remaining > 0,
            "issuer": issuer.get("organizationName", issuer.get("commonName", "Unknown")),
            "subject": subject.get("commonName", domain),
            "expires_on": expires_dt.strftime("%Y-%m-%d"),
            "days_remaining": days_remaining,
        })
    except (socket.timeout, socket.gaierror, ConnectionRefusedError) as e:
        result["error"] = f"Could not connect to {domain}: {e}"
    except ssl.SSLCertVerificationError as e:
        result["error"] = f"Certificate verification failed: {e}"
        result["valid"] = False
    except Exception as e:  # noqa: BLE001 - surface any unexpected error to the UI
        logger.warning("SSL check failed for %s: %s", domain, e)
        result["error"] = str(e)

    return result

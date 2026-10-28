"""HMAC signing for ProbeHarbor inbound webhooks."""

from __future__ import annotations

import hashlib
import hmac


def sign_body(secret: str, body: str) -> str:
    digest = hmac.new(
        secret.encode("utf-8"),
        body.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return f"sha256={digest}"


def sign_timestamped(secret: str, body: str, timestamp: str) -> str:
    """V2 signature: HMAC-SHA256 of "<timestamp>.<body>".

    ProbeHarbor rejects V2 requests whose X-ProbeHarbor-Timestamp is more than
    5 minutes from its clock, so a captured request can't be replayed later.
    """
    digest = hmac.new(
        secret.encode("utf-8"),
        f"{timestamp}.{body}".encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return f"sha256={digest}"

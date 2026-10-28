"""Tests for ProbeHarbor signing helper."""

from __future__ import annotations

import hashlib
import hmac
import importlib.util
from pathlib import Path


def _signing_module():
    path = (
        Path(__file__).resolve().parents[1]
        / "custom_components"
        / "thermaltrace"
        / "signing.py"
    )
    spec = importlib.util.spec_from_file_location("thermaltrace_signing", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _sign_body(secret: str, body: str) -> str:
    return _signing_module().sign_body(secret, body)


def test_sign_body_matches_thermaltrace_format() -> None:
    secret = "gts_testsecret"
    body = '{"action":"snooze","hours":24}'
    expected = hmac.new(
        secret.encode(),
        body.encode(),
        hashlib.sha256,
    ).hexdigest()
    assert _sign_body(secret, body) == f"sha256={expected}"


def test_sign_timestamped_matches_probeharbor_server() -> None:
    # Vector produced by ProbeHarbor's own timestampedSignatureHeaders()
    # (src/lib/webhookSigning.ts) for this secret, body and timestamp.
    signature = _signing_module().sign_timestamped(
        "gts_test_secret", '{"action":"snooze","hours":4}', "1761650000"
    )
    assert signature == "sha256=2169b10609a2101a8d0cab9464720f39131af4079d4b24f45e9eacf6028e069c"


def test_sign_timestamped_depends_on_the_timestamp() -> None:
    module = _signing_module()
    body = '{"action":"status"}'
    assert module.sign_timestamped("s", body, "1") != module.sign_timestamped("s", body, "2")

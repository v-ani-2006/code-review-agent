"""Mock webhook dispatcher and receiver for outbound webhook delivery testing."""
import hashlib
import hmac
import json
from typing import Any, Dict, List, Optional


class MockWebhookReceiver:
    """Mock receiver capturing outbound webhook events and simulating destination response."""

    def __init__(self, response_status: int = 200, simulate_error: bool = False):
        self.response_status = response_status
        self.simulate_error = simulate_error
        self.received_events: List[Dict[str, Any]] = []

    async def handle_delivery(
        self,
        url: str,
        payload: Dict[str, Any],
        signature: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Process dispatched webhook delivery."""
        if self.simulate_error:
            raise ConnectionError(f"Failed to connect to webhook endpoint: {url}")

        event_record = {
            "url": url,
            "payload": payload,
            "signature": signature,
            "headers": headers or {},
            "status_code": self.response_status,
        }
        self.received_events.append(event_record)
        return {"status_code": self.response_status, "success": 200 <= self.response_status < 300}

    @staticmethod
    def verify_signature(payload_bytes: bytes, secret: str, received_signature: str) -> bool:
        """Verify HMAC-SHA256 signature against received header."""
        expected_sig = hmac.new(
            secret.encode("utf-8"),
            payload_bytes,
            hashlib.sha256,
        ).hexdigest()
        clean_sig = received_signature.replace("sha256=", "").strip()
        return hmac.compare_digest(expected_sig, clean_sig)

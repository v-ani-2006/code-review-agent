import asyncio
from datetime import datetime, timezone
import hashlib
import hmac
import json
import time
from typing import Any, Dict, Optional, Tuple
import uuid
import httpx

from app.core.config import settings
from app.core.logging import logger


def generate_webhook_signature(payload_bytes: bytes, secret: str) -> str:
    """Compute HMAC-SHA256 cryptographic signature for the raw payload bytes."""
    secret_key = secret.encode("utf-8")
    mac = hmac.new(secret_key, msg=payload_bytes, digestmod=hashlib.sha256)
    return mac.hexdigest()


async def dispatch_webhook_request(
    url: str,
    secret: str,
    event_type: str,
    payload_data: Dict[str, Any],
    max_retries: int = 3,
    timeout_seconds: float = 5.0,
) -> Tuple[bool, int, Optional[str]]:
    """Send an authenticated, signed webhook POST request with exponential retry backoff."""
    delivery_id = str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc).isoformat()

    envelope = {
        "id": delivery_id,
        "event": event_type,
        "timestamp": timestamp,
        "data": payload_data,
    }
    payload_bytes = json.dumps(envelope, default=str).encode("utf-8")
    signature = generate_webhook_signature(payload_bytes, secret)

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "CodePilot-Webhook-Engine/1.0",
        "X-CodePilot-Delivery-ID": delivery_id,
        "X-CodePilot-Event": event_type,
        "X-CodePilot-Timestamp": timestamp,
        "X-CodePilot-Signature": f"sha256={signature}",
    }

    last_error: Optional[str] = None
    last_status = 0

    for attempt in range(1, max_retries + 1):
        try:
            async with httpx.AsyncClient(timeout=timeout_seconds) as client:
                response = await client.post(url, content=payload_bytes, headers=headers)
                last_status = response.status_code
                if 200 <= response.status_code < 300:
                    logger.info(
                        " Webhook delivered successfully to %s [Event: %s, Attempt: %d, Status: %d]",
                        url,
                        event_type,
                        attempt,
                        response.status_code,
                    )
                    return True, response.status_code, response.text[:500]
                else:
                    last_error = f"HTTP {response.status_code}: {response.text[:200]}"
                    logger.warning(
                        "⚠️ Webhook delivery warning to %s [Status: %d, Attempt: %d/%d]",
                        url,
                        response.status_code,
                        attempt,
                        max_retries,
                    )
        except Exception as exc:
            last_error = str(exc)
            logger.warning(
                "⚠️ Webhook connection attempt %d/%d failed for %s: %s",
                attempt,
                max_retries,
                url,
                str(exc),
            )

        if attempt < max_retries:
            await asyncio.sleep(2 ** (attempt - 1))  # 1s, 2s

    return False, last_status, last_error

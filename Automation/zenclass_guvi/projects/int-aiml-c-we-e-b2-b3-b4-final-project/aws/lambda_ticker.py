"""AWS Lambda Ball-by-Ball Ticker Handler (Emits 1 Delivery / 20s to Game-State FastAPI Service)."""

from __future__ import annotations

import json
import os
import urllib.request
from typing import Any, Dict


def lambda_handler(event: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
    """Triggered by EventBridge every 20 seconds to advance the active match replay by 1 ball."""
    service_url = os.getenv("GAME_STATE_API_URL", "http://localhost:8000")
    match_id = event.get("match_id") or os.getenv("ACTIVE_MATCH_ID", "981019")
    language = event.get("language", "English")

    payload = json.dumps({"match_id": match_id, "steps": 1, "language": language}).encode("utf-8")
    req = urllib.request.Request(
        f"{service_url.rstrip('/')}/replay/step",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    return {"statusCode": 200, "body": body}

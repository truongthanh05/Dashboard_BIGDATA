from __future__ import annotations
import requests

def _base(url: str) -> str:
    return url.rstrip("/")

def check_api_health(api_base_url: str, timeout: float = 2.0):
    try:
        response = requests.get(f"{_base(api_base_url)}/health", timeout=timeout)
        data = response.json()
        if not response.ok: return False, data
        return data.get("model_ready") is True, data
    except (requests.RequestException, ValueError) as exc:
        return False, str(exc)

def predict_cost(api_base_url: str, payload: dict, timeout: float = 30.0):
    try:
        response = requests.post(f"{_base(api_base_url)}/predict", json=payload, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        if "predicted_total_claim_cost" not in data:
            return None, "API không trả predicted_total_claim_cost"
        return data, None
    except (requests.RequestException, ValueError) as exc:
        return None, str(exc)

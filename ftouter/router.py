import os
import requests

from .providers import PROVIDER_INFO
from . import chat_models, reasoning_models, tool_calling_models, vision_models


def _configured_by_provider():
    configured = {}
    for module in (chat_models, reasoning_models, tool_calling_models, vision_models):
        for provider, model_id in module.MODELS:
            configured.setdefault(provider, set()).add(model_id)
    return configured


def check_available_models():
    configured = _configured_by_provider()
    results = {}
    for provider, model_ids in configured.items():
        info = PROVIDER_INFO[provider]
        key = os.getenv(info["env_key"])
        if not key:
            results[provider] = {"status": "no_key"}
            continue
        try:
            resp = requests.get(
                f"{info['base_url']}/models",
                headers={"Authorization": f"Bearer {key}"},
                timeout=10,
            )
            resp.raise_for_status()
            live_ids = {m["id"] for m in resp.json()["data"]}
            results[provider] = {
                "status": "ok",
                "missing": sorted(model_ids - live_ids),
            }
        except Exception as e:
            results[provider] = {"status": "error", "error": str(e)}
    return results

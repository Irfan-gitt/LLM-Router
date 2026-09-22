import os
import time
import requests

from .providers import PROVIDER_INFO

MODELS = [
    ("groq", "qwen/qwen3.8-27b"),
    ("groq", "openai/gpt-oss-120b"),
    ("groq", "openai/gpt-oss-20b"),
    ("groq", "allam-2-7b"),
    ("openrouter", "google/gemma-4-26b-a4b-it:free"),
    ("openrouter", "google/gemma-4-31b-it:free"),
    ("openrouter", "nvidia/nemotron-3-super-120b-a12b:free"),
    ("openrouter", "nvidia/nemotron-3.5-lightning:free"),
    ("openrouter", "liquid/lfm-2.5-2.6b:free"),
    ("mistral", "magistral-medium-latest"),
]

COOLDOWN_SECONDS = 30 * 60
_cooldown = {}  # (provider, model_id) -> unix time it's allowed again


def _reason(status_code):
    if status_code in (401, 403):
        return "auth failed — check your API key"
    if status_code == 404:
        return "model not found — likely deprecated or renamed"
    if status_code == 429:
        return "rate limited — out of free quota"
    if status_code and status_code >= 500:
        return "provider server error — try again later"
    return f"request failed (status {status_code})"


def complete(messages, **kwargs):
    now = time.time()
    for provider, model_id in MODELS:
        if _cooldown.get((provider, model_id), 0) > now:
            continue

        info = PROVIDER_INFO[provider]
        key = os.getenv(info["env_key"])
        if not key:
            continue

        try:
            resp = requests.post(
                f"{info['base_url']}/chat/completions",
                headers={"Authorization": f"Bearer {key}"},
                json={"model": model_id, "messages": messages, **kwargs},
                timeout=30,
            )
            if resp.status_code == 200:
                return resp.json()

            reason = _reason(resp.status_code)
            print(f"{provider}/{model_id} failed: {reason}")
            _cooldown[(provider, model_id)] = now + COOLDOWN_SECONDS

        except requests.exceptions.RequestException as e:
            print(f"{provider}/{model_id} failed: network error — {e}")
            _cooldown[(provider, model_id)] = now + COOLDOWN_SECONDS

    raise RuntimeError(
        "all chat models are currently unavailable or on cooldown")

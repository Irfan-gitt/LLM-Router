# ftouter

A resilient runtime layer for free and cheap-tier LLM APIs.

Free-tier LLM providers are unreliable in ways that break production apps silently: models get deprecated overnight, quotas zero out without warning, and providers add card requirements with no notice. `ftouter` sits between your app and multiple providers, automatically falling back to the next available model when one fails — so a single dead endpoint doesn't take down your whole app.

## Features

- **Automatic fallback** across multiple providers and models
- **Cooldown handling** — a model that fails gets temporarily skipped instead of retried every call
- **Clear failure reasons** — distinguishes rate limits, deprecated models, bad keys, and server errors instead of generic exceptions
- **Zero config to start** — just add your API keys and call `.complete()`
- Five ready-made routers for different use cases: `chat_models`, `general_models`, `reasoning_models`, `tool_call_models`, `vision_models`

## Installation

```bash
pip install ftouter
```

## Quickstart

1. Create a `.env` file in your project root with the API keys for the providers you want to use:

```env
GROQ_API_KEY=your_key_here
OPENROUTER_API_KEY=your_key_here
MISTRAL_API_KEY=your_key_here
```

You don't need all three — `ftouter` skips any provider whose key isn't set and falls through to the next one.

2. Use it in your code:

```python
from ftouter import chat_models
from dotenv import load_dotenv

load_dotenv()

result = chat_models.complete([
    {"role": "user", "content": "Say hi in 5 words"}
])

print(result["choices"][0]["message"]["content"])
```

## Available routers

| Router | Use case |
|---|---|
| `chat_models.complete()` | General-purpose conversational completions |
| `general_models.complete()` | General-purpose tasks, pooled across all other routers |
| `reasoning_models.complete()` | Tasks that benefit from reasoning-focused models |
| `tool_call_models.complete()` | Completions that use function/tool calling |
| `vision_models.complete()` | Completions that include image input |

Each router tries a prioritized list of models across providers and automatically moves to the next one on failure.

## Vision

`vision_models.complete()` takes the same message format as the others — an image is just another block inside `content`, either an `https://` URL or a base64 `data:` URI:

```python
import base64
from ftouter import vision_models
from dotenv import load_dotenv

load_dotenv()

with open("example.jpg", "rb") as image_file:
    image_data = base64.b64encode(image_file.read()).decode("utf-8")

result = vision_models.complete([
    {
        "role": "user",
        "content": [
            {"type": "text", "text": "what's in this image?"},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image_data}"
                }
            }
        ]
    }
])
print(result["choices"][0]["message"]["content"])
```

Vision draws from Groq, OpenRouter, and Mistral like the other routers, plus two vision-specific providers — add their keys to `.env` only if you want them in the fallback chain, `ftouter` skips them otherwise like any other missing key:

```env
GEMINI_API_KEY=your_key_here
MOONDREAM_API_KEY=your_key_here
```

Note: base64 image support is confirmed for Groq and Gemini. OpenRouter should accept it (same spec, not independently verified here). Moondream's exact behavior with base64 input is unconfirmed — test it directly if you're relying on that provider.

## How fallback works

When you call `.complete()`, `ftouter`:

1. Tries the first available (not-on-cooldown) model in its list
2. If it fails, records *why* (rate limit, deprecated model, bad key, server error, etc.) and puts that model on a cooldown timer
3. Moves to the next model and repeats
4. Returns the first successful response
5. Raises `RuntimeError` only if every model in the list is exhausted or on cooldown

This means a single provider having a bad day doesn't crash your app — it just quietly routes around it.

## Getting free API keys

- **Groq** — [console.groq.com](https://console.groq.com)
- **OpenRouter** — [openrouter.ai](https://openrouter.ai)
- **Mistral** — [console.mistral.ai](https://console.mistral.ai)
- **Gemini** (vision only) — [aistudio.google.com](https://aistudio.google.com)
- **Moondream** (vision only) — [moondream.ai](https://moondream.ai)

## Handling errors

If every provider fails, `.complete()` raises a `RuntimeError`:

```python
try:
    result = chat_models.complete([{"role": "user", "content": "Hello"}])
    print(result["choices"][0]["message"]["content"])
except RuntimeError as e:
    print(f"All providers failed: {e}")
```

## Contributing

Issues and pull requests are welcome. If you'd like to add support for another provider, open an issue first so the model list and provider config stay consistent.

https://github.com/Irfan-gitt

## License

MIT
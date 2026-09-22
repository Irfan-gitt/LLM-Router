# ftouter

A resilient runtime layer for free and cheap-tier LLM APIs.

Free-tier LLM providers are unreliable in ways that break production apps silently: models get deprecated overnight, quotas zero out without warning, and providers add card requirements with no notice. `ftouter` sits between your app and multiple providers, automatically falling back to the next available model when one fails — so a single dead endpoint doesn't take down your whole app.

## Features

- **Automatic fallback** across multiple providers and models
- **Cooldown handling** — a model that fails gets temporarily skipped instead of retried every call
- **Clear failure reasons** — distinguishes rate limits, deprecated models, bad keys, and server errors instead of generic exceptions
- **Zero config to start** — just add your API keys and call `.complete()`
- Four ready-made routers for different use cases: `chat`, `general`, `reasoning`, `tool_call`

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
from ftouter import chat
from dotenv import load_dotenv

load_dotenv()

result = chat.complete([
    {"role": "user", "content": "Say hi in 5 words"}
])

print(result["choices"][0]["message"]["content"])
```

## Available routers

| Router | Use case |
|---|---|
| `chat.complete()` | General-purpose conversational completions |
| `general.complete()` | General-purpose tasks |
| `reasoning.complete()` | Tasks that benefit from reasoning-focused models |
| `tool_call.complete()` | Completions that use function/tool calling |

Each router tries a prioritized list of models across providers and automatically moves to the next one on failure.

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

## Handling errors

If every provider fails, `.complete()` raises a `RuntimeError`:

```python
try:
    result = chat.complete([{"role": "user", "content": "Hello"}])
    print(result["choices"][0]["message"]["content"])
except RuntimeError as e:
    print(f"All providers failed: {e}")
```

## Contributing

Issues and pull requests are welcome. If you'd like to add support for another provider, open an issue first so the model list and provider config stay consistent.

## License

MIT
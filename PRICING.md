# API pricing and token usage

The benchmark reports **input** and **output** token counts for each run. Use each provider’s pricing page to estimate cost from these numbers.

## Default providers (Gemini, DeepSeek, Kimi)

| Provider | Pricing page | Notes |
|----------|--------------|--------|
| **Gemini** | [Google AI pricing](https://ai.google.dev/pricing) | Per 1M input/output tokens; free tier available. |
| **DeepSeek** | [DeepSeek API pricing](https://platform.deepseek.com/pricing) | Per 1M tokens; deepseek-chat, deepseek-reasoner. |
| **Kimi (Moonshot)** | [Moonshot pricing](https://platform.moonshot.ai/docs/pricing) or console | Per 1M tokens; moonshot-v1-8k, kimi-k2-* models. |

## Optional providers

| Provider | Pricing page |
|----------|--------------|
| **OpenAI** | [OpenAI pricing](https://openai.com/api/pricing/) |
| **Anthropic** | [Anthropic pricing](https://www.anthropic.com/pricing) |

## How token counts are used

- **Single run:** `run_audit.py` prints `Tokens: input=… output=…` after the run.
- **Compare:** `run_audit.py --compare` prints a **Token usage** section with input/output totals per provider×model (summed over all prompts and samples).

Multiply your token totals by the provider’s per‑million rate to estimate cost.

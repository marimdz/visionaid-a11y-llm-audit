"""
LLM client abstraction and provider implementations.

Primary providers (cost-effective): Gemini, DeepSeek, Kimi.
Optional: OpenAI, Anthropic. Set the corresponding API key in env.
"""
from __future__ import annotations

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


@dataclass
class LLMResponse:
    """Raw response from an LLM."""
    content: str
    model: str
    provider: str
    finish_reason: str | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None


class BaseLLM(ABC):
    """Abstract LLM client."""

    @property
    @abstractmethod
    def provider(self) -> str:
        ...

    @property
    @abstractmethod
    def default_model(self) -> str:
        ...

    @abstractmethod
    def complete(self, prompt: str, *, model: str | None = None, max_tokens: int = 2048) -> LLMResponse:
        ...


def _openai_completion(
    base_url: str | None,
    api_key: str,
    model: str,
    prompt: str,
    max_tokens: int,
    provider_label: str,
) -> LLMResponse:
    """Shared OpenAI-compatible API call. base_url=None means OpenAI."""
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError("Install openai: pip install openai") from None
    kwargs = {"api_key": api_key}
    if base_url:
        kwargs["base_url"] = base_url
    client = OpenAI(**kwargs)
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
    )
    choice = resp.choices[0]
    usage = getattr(resp, "usage", None)
    in_tok = getattr(usage, "prompt_tokens", None) or getattr(usage, "input_tokens", None) if usage else None
    out_tok = getattr(usage, "completion_tokens", None) or getattr(usage, "output_tokens", None) if usage else None
    return LLMResponse(
        content=choice.message.content or "",
        model=model,
        provider=provider_label,
        finish_reason=getattr(choice, "finish_reason", None),
        input_tokens=in_tok,
        output_tokens=out_tok,
    )


class OpenAILLM(BaseLLM):
    """OpenAI API (GPT-4, etc.)."""

    def __init__(self, model: str = "gpt-4o-mini", api_key: str | None = None):
        self._model = model
        self._api_key = api_key or os.environ.get("OPENAI_API_KEY")

    @property
    def provider(self) -> str:
        return "openai"

    @property
    def default_model(self) -> str:
        return self._model

    def complete(self, prompt: str, *, model: str | None = None, max_tokens: int = 2048) -> LLMResponse:
        if not self._api_key:
            raise ValueError("OPENAI_API_KEY not set")
        return _openai_completion(
            base_url=None,
            api_key=self._api_key,
            model=model or self._model,
            prompt=prompt,
            max_tokens=max_tokens,
            provider_label=self.provider,
        )


class DeepSeekLLM(BaseLLM):
    """DeepSeek API (OpenAI-compatible)."""

    def __init__(self, model: str = "deepseek-chat", api_key: str | None = None):
        self._model = model
        self._api_key = api_key or os.environ.get("DEEPSEEK_API_KEY")

    @property
    def provider(self) -> str:
        return "deepseek"

    @property
    def default_model(self) -> str:
        return self._model

    def complete(self, prompt: str, *, model: str | None = None, max_tokens: int = 2048) -> LLMResponse:
        if not self._api_key:
            raise ValueError("DEEPSEEK_API_KEY not set")
        return _openai_completion(
            base_url="https://api.deepseek.com/v1",
            api_key=self._api_key,
            model=model or self._model,
            prompt=prompt,
            max_tokens=max_tokens,
            provider_label=self.provider,
        )


class KimiLLM(BaseLLM):
    """Kimi / Moonshot API (OpenAI-compatible)."""

    def __init__(self, model: str = "moonshot-v1-8k", api_key: str | None = None):
        self._model = model
        self._api_key = api_key or os.environ.get("MOONSHOT_API_KEY") or os.environ.get("KIMI_API_KEY")

    @property
    def provider(self) -> str:
        return "kimi"

    @property
    def default_model(self) -> str:
        return self._model

    def complete(self, prompt: str, *, model: str | None = None, max_tokens: int = 2048) -> LLMResponse:
        if not self._api_key:
            raise ValueError("MOONSHOT_API_KEY or KIMI_API_KEY not set")
        return _openai_completion(
            base_url="https://api.moonshot.ai/v1",
            api_key=self._api_key,
            model=model or self._model,
            prompt=prompt,
            max_tokens=max_tokens,
            provider_label=self.provider,
        )


class GeminiLLM(BaseLLM):
    """Google Gemini API."""

    def __init__(self, model: str = "gemini-2.0-flash", api_key: str | None = None):
        self._model = model
        self._api_key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

    @property
    def provider(self) -> str:
        return "gemini"

    @property
    def default_model(self) -> str:
        return self._model

    def complete(self, prompt: str, *, model: str | None = None, max_tokens: int = 2048) -> LLMResponse:
        if not self._api_key:
            raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY not set")
        try:
            from google import genai
        except ImportError:
            raise ImportError("Install google-genai: pip install google-genai") from None
        client = genai.Client(api_key=self._api_key)
        model = model or self._model
        from google.genai import types
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(max_output_tokens=max_tokens),
        )
        text = ""
        if response.candidates:
            for part in response.candidates[0].content.parts or []:
                if hasattr(part, "text") and part.text:
                    text += part.text
        usage = getattr(response, "usage_metadata", None)
        in_tok = (getattr(usage, "prompt_token_count", None) or getattr(usage, "prompt_tokens", None)) if usage else None
        out_tok = (getattr(usage, "candidates_token_count", None) or getattr(usage, "completion_tokens", None) or getattr(usage, "output_tokens", None)) if usage else None
        return LLMResponse(
            content=text,
            model=model,
            provider=self.provider,
            finish_reason=None,
            input_tokens=in_tok,
            output_tokens=out_tok,
        )


class AnthropicLLM(BaseLLM):
    """Anthropic API (Claude)."""

    def __init__(self, model: str = "claude-3-5-haiku-20241022", api_key: str | None = None):
        self._model = model
        self._api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")

    @property
    def provider(self) -> str:
        return "anthropic"

    @property
    def default_model(self) -> str:
        return self._model

    def complete(self, prompt: str, *, model: str | None = None, max_tokens: int = 2048) -> LLMResponse:
        if not self._api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")
        try:
            from anthropic import Anthropic
        except ImportError:
            raise ImportError("Install anthropic: pip install anthropic") from None
        client = Anthropic(api_key=self._api_key)
        model = model or self._model
        msg = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        text = ""
        if msg.content:
            for block in msg.content:
                if hasattr(block, "text"):
                    text += block.text
        usage = getattr(msg, "usage", None)
        in_tok = getattr(usage, "input_tokens", None) if usage else None
        out_tok = getattr(usage, "output_tokens", None) if usage else None
        return LLMResponse(
            content=text,
            model=model,
            provider=self.provider,
            finish_reason=getattr(msg, "stop_reason", None),
            input_tokens=in_tok,
            output_tokens=out_tok,
        )


def get_llm(provider: str, model: str | None = None) -> BaseLLM:
    """Factory. Default providers: gemini, deepseek, kimi. Also: openai, anthropic."""
    if provider == "openai":
        return OpenAILLM(model=model or "gpt-4o-mini")
    if provider == "anthropic":
        return AnthropicLLM(model=model or "claude-3-5-haiku-20241022")
    if provider == "gemini":
        return GeminiLLM(model=model or "gemini-2.0-flash")
    if provider == "deepseek":
        return DeepSeekLLM(model=model or "deepseek-chat")
    if provider == "kimi":
        return KimiLLM(model=model or "moonshot-v1-8k")
    raise ValueError(f"Unknown provider: {provider}")

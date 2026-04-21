"""AI provider abstraction — supports OpenAI, Anthropic, and local/custom endpoints."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import httpx
from openai import OpenAI

from rational_ai.config import AIProviderConfig


@dataclass
class AIResponse:
    content: str
    model: str
    usage: dict[str, int]
    raw: Any = None


class AIProvider:
    """Unified interface to LLM providers."""

    def __init__(self, config: AIProviderConfig):
        self.config = config
        self._client: OpenAI | None = None

    @property
    def client(self) -> OpenAI:
        if self._client is None:
            kwargs: dict[str, Any] = {"api_key": self.config.api_key}
            if self.config.base_url:
                kwargs["base_url"] = self.config.base_url
            elif self.config.provider == "anthropic":
                kwargs["base_url"] = "https://api.anthropic.com/v1"
            self._client = OpenAI(**kwargs)
        return self._client

    def chat(
        self,
        system: str,
        user: str,
        temperature: float | None = None,
        max_tokens: int | None = None,
        response_format: dict | None = None,
    ) -> AIResponse:
        """Send a chat completion request."""
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]
        kwargs: dict[str, Any] = {
            "model": self.config.model,
            "messages": messages,
            "temperature": temperature or self.config.temperature,
            "max_tokens": max_tokens or self.config.max_tokens,
        }
        if response_format:
            kwargs["response_format"] = response_format

        resp = self.client.chat.completions.create(**kwargs)
        choice = resp.choices[0]
        return AIResponse(
            content=choice.message.content or "",
            model=resp.model,
            usage={
                "prompt_tokens": resp.usage.prompt_tokens if resp.usage else 0,
                "completion_tokens": resp.usage.completion_tokens if resp.usage else 0,
            },
            raw=resp,
        )

    def chat_json(self, system: str, user: str, **kwargs) -> dict:
        """Chat expecting JSON response."""
        resp = self.chat(
            system=system + "\n\nRespond with valid JSON only.",
            user=user,
            response_format={"type": "json_object"},
            **kwargs,
        )
        return json.loads(resp.content)

    def generate_mermaid(self, description: str, diagram_type: str = "flowchart") -> str:
        """Generate a Mermaid diagram from a description."""
        resp = self.chat(
            system=(
                "You are a software architecture diagram expert. "
                "Generate valid Mermaid diagram code. Return ONLY the Mermaid code, "
                "no markdown fences or explanations."
            ),
            user=f"Create a {diagram_type} diagram for:\n{description}",
        )
        code = resp.content.strip()
        # Strip markdown fences if present
        if code.startswith("```"):
            lines = code.split("\n")
            lines = [l for l in lines if not l.startswith("```")]
            code = "\n".join(lines)
        return code

"""Configuration management for Rational AI."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml


RAI_DIR = ".rai"
PROJECT_FILE = "project.yaml"
CONFIG_FILE = "config.yaml"


@dataclass
class AIProviderConfig:
    provider: str = "openai"  # openai | anthropic | local
    model: str = "gpt-4o"
    api_key: str = ""
    base_url: str = ""
    temperature: float = 0.7
    max_tokens: int = 4096


@dataclass
class Config:
    ai: AIProviderConfig = field(default_factory=AIProviderConfig)
    project_dir: Path = field(default_factory=lambda: Path.cwd())

    @property
    def rai_dir(self) -> Path:
        return self.project_dir / RAI_DIR

    @property
    def project_file(self) -> Path:
        return self.rai_dir / PROJECT_FILE

    @property
    def config_file(self) -> Path:
        return self.rai_dir / CONFIG_FILE

    def ensure_dirs(self) -> None:
        self.rai_dir.mkdir(parents=True, exist_ok=True)
        for sub in ["requirements", "architecture", "roles", "development", "deployment", "schedule"]:
            (self.rai_dir / sub).mkdir(exist_ok=True)


def load_config(project_dir: Path | None = None) -> Config:
    """Load configuration from .rai/config.yaml or create defaults."""
    base = project_dir or Path.cwd()
    config_path = base / RAI_DIR / CONFIG_FILE

    cfg = Config(project_dir=base)

    if config_path.exists():
        raw = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
        ai_raw = raw.get("ai", {})
        cfg.ai = AIProviderConfig(
            provider=ai_raw.get("provider", "openai"),
            model=ai_raw.get("model", "gpt-4o"),
            api_key=ai_raw.get("api_key", ""),
            base_url=ai_raw.get("base_url", ""),
            temperature=ai_raw.get("temperature", 0.7),
            max_tokens=ai_raw.get("max_tokens", 4096),
        )

    # Environment overrides
    if key := os.environ.get("RAI_API_KEY"):
        cfg.ai.api_key = key
    if provider := os.environ.get("RAI_PROVIDER"):
        cfg.ai.provider = provider
    if model := os.environ.get("RAI_MODEL"):
        cfg.ai.model = model

    return cfg


def save_config(cfg: Config) -> None:
    """Persist config to .rai/config.yaml."""
    cfg.ensure_dirs()
    data = {
        "ai": {
            "provider": cfg.ai.provider,
            "model": cfg.ai.model,
            "base_url": cfg.ai.base_url,
            "temperature": cfg.ai.temperature,
            "max_tokens": cfg.ai.max_tokens,
            # api_key intentionally excluded from file — use env var
        }
    }
    cfg.config_file.write_text(yaml.dump(data, default_flow_style=False), encoding="utf-8")

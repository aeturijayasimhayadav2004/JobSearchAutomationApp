"""Configuration models for the Job Search Automation application."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Optional


@dataclass(slots=True)
class ResumeConfig:
    """Configuration for loading and parsing the resume."""

    path: Path
    chunk_size: int = 400
    chunk_overlap: int = 50


@dataclass(slots=True)
class JobSearchConfig:
    """Configuration for job search providers."""

    provider: str
    keywords: list[str]
    location: Optional[str] = None
    max_results: int = 20
    filters: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class LLMConfig:
    """Configuration for connecting to an LLM provider."""

    provider: str = "openai"
    model: str = "gpt-4o-mini"
    temperature: float = 0.1
    max_tokens: int = 512
    api_key_env: str = "OPENAI_API_KEY"


@dataclass(slots=True)
class AutomationConfig:
    """Top-level configuration for orchestrating the automation pipeline."""

    resume: ResumeConfig
    job_search: JobSearchConfig
    llm: LLMConfig
    notify_emails: Iterable[str] = field(default_factory=tuple)


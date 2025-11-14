"""Job Search Automation package."""
from .automation import JobSearchAutomator, AutomationReport
from .config import AutomationConfig, JobSearchConfig, LLMConfig, ResumeConfig
from .resume_parser import ResumeParser
from .retriever import ResumeRetriever
from .matcher import JobMatcher, MatchSettings
from .llm import LLMClient
from .apply import JobApplicationService
from .job_fetchers.base import JobFetcher, StaticJobFetcher
from .job_fetchers.local import LocalJobFetcher
from .job_fetchers.serpapi import SerpApiJobFetcher

try:  # pragma: no cover - optional dependency
    from .webapp import create_app
except ModuleNotFoundError as exc:  # pragma: no cover - used when Flask is missing
    def create_app(*_: object, **__: object) -> None:  # type: ignore[override]
        raise RuntimeError(
            "Flask is required to use the bundled web application. Install it with 'pip install flask'."
        ) from exc

__all__ = [
    "AutomationReport",
    "AutomationConfig",
    "JobSearchConfig",
    "LLMConfig",
    "ResumeConfig",
    "JobSearchAutomator",
    "ResumeParser",
    "ResumeRetriever",
    "JobMatcher",
    "MatchSettings",
    "LLMClient",
    "JobApplicationService",
    "JobFetcher",
    "StaticJobFetcher",
    "SerpApiJobFetcher",
    "LocalJobFetcher",
    "create_app",
]

"""Implementation of a job fetcher using SerpAPI's Google Jobs engine."""
from __future__ import annotations

import os
from datetime import datetime
from typing import Iterable

from ..config import JobSearchConfig
from ..models import JobPosting
from .base import JobFetcher

try:  # pragma: no cover - optional dependency
    import requests
except Exception:  # pragma: no cover - library optional
    requests = None  # type: ignore

SERPAPI_URL = "https://serpapi.com/search.json"


class SerpApiJobFetcher(JobFetcher):
    """Fetch job listings from SerpAPI's Google Jobs integration."""

    def __init__(self, config: JobSearchConfig, api_key_env: str = "SERPAPI_API_KEY") -> None:
        self.config = config
        self.api_key_env = api_key_env

    def search(self) -> Iterable[JobPosting]:
        api_key = os.getenv(self.api_key_env)
        if not api_key:
            raise RuntimeError(
                f"Missing SerpAPI API key. Set the {self.api_key_env} environment variable."
            )

        params = {
            "engine": "google_jobs",
            "q": " ".join(self.config.keywords),
            "hl": "en",
            "api_key": api_key,
            "num": self.config.max_results,
        }
        if self.config.location:
            params["location"] = self.config.location
        params.update(self.config.filters)

        if requests is None:
            raise RuntimeError(
                "The 'requests' package is required to use the SerpAPI job fetcher. Install it with 'pip install requests'."
            )

        response = requests.get(SERPAPI_URL, params=params, timeout=20)
        response.raise_for_status()
        data = response.json()
        for result in data.get("jobs_results", []):
            yield self._to_job_posting(result)

    def _to_job_posting(self, payload: dict) -> JobPosting:
        posted_at = None
        if date_str := payload.get("detected_extensions", {}).get("posted_at"):
            try:
                posted_at = datetime.fromisoformat(date_str)
            except ValueError:
                posted_at = None

        return JobPosting(
            title=payload.get("title", ""),
            company=payload.get("company_name", ""),
            description=payload.get("description", ""),
            url=payload.get("apply_link") or payload.get("related_links", [{}])[0].get("link", ""),
            location=payload.get("location"),
            salary=payload.get("detected_extensions", {}).get("salary"),
            source="serpapi",
            posted_at=posted_at,
        )

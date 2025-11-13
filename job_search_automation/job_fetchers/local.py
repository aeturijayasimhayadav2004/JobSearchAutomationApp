"""Local job fetcher backed by a bundled JSON dataset."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from ..config import JobSearchConfig
from ..models import JobPosting
from .base import JobFetcher


class LocalJobFetcher(JobFetcher):
    """Load job postings from a JSON file for offline demos."""

    def __init__(self, config: JobSearchConfig, dataset_path: Path | None = None) -> None:
        self.config = config
        self.dataset_path = dataset_path or Path(__file__).resolve().parent.parent / "sample_data" / "jobs.json"

    def search(self) -> Iterable[JobPosting]:
        if not self.dataset_path.exists():
            raise FileNotFoundError(
                f"Local job dataset not found at {self.dataset_path}."
            )

        data = json.loads(self.dataset_path.read_text(encoding="utf-8"))
        keywords = {keyword.lower() for keyword in self.config.keywords}
        location_filter = (self.config.location or "").lower()

        count = 0
        for payload in data:
            job = JobPosting(
                title=payload.get("title", ""),
                company=payload.get("company", ""),
                description=payload.get("description", ""),
                url=payload.get("url", ""),
                location=payload.get("location"),
                salary=payload.get("salary"),
                source="local",
            )

            if keywords and not self._matches_keywords(job, keywords):
                continue

            if location_filter and location_filter not in (job.location or "").lower():
                continue

            yield job
            count += 1
            if count >= self.config.max_results:
                break

    def _matches_keywords(self, job: JobPosting, keywords: set[str]) -> bool:
        haystack = f"{job.title}\n{job.description}".lower()
        return any(keyword in haystack for keyword in keywords)

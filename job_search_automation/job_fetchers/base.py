"""Base classes and utilities for fetching job listings."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable

from ..models import JobPosting


class JobFetcher(ABC):
    """Abstract base class for job listing providers."""

    @abstractmethod
    def search(self) -> Iterable[JobPosting]:
        """Yield job postings matching the configured criteria."""


class StaticJobFetcher(JobFetcher):
    """Returns pre-defined job postings. Useful for testing and demos."""

    def __init__(self, jobs: Iterable[JobPosting]) -> None:
        self._jobs = tuple(jobs)

    def search(self) -> Iterable[JobPosting]:
        yield from self._jobs

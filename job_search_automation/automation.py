"""High-level orchestration for the job search automation pipeline."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from .apply import JobApplicationService
from .config import AutomationConfig
from .job_fetchers.base import JobFetcher
from .matcher import JobMatcher
from .models import ApplicationResult, MatchingResult
from .resume_parser import ResumeParser


@dataclass(slots=True)
class AutomationReport:
    matched_jobs: Sequence[MatchingResult]
    applications: Sequence[ApplicationResult]


class JobSearchAutomator:
    """Coordinates fetching jobs, matching, and applying."""

    def __init__(
        self,
        config: AutomationConfig,
        resume_parser: ResumeParser,
        job_fetcher: JobFetcher,
        matcher: JobMatcher,
        application_service: JobApplicationService,
    ) -> None:
        self.config = config
        self.resume_parser = resume_parser
        self.job_fetcher = job_fetcher
        self.matcher = matcher
        self.application_service = application_service

    def run(self) -> AutomationReport:
        resume = self.resume_parser.load(self.config.resume.path)
        profile = self.resume_parser.extract_profile(resume)
        self.matcher.prepare(
            resume,
            chunk_size=self.config.resume.chunk_size,
            overlap=self.config.resume.chunk_overlap,
        )

        jobs = list(self.job_fetcher.search())
        matches = self.matcher.score_jobs(jobs)

        applications: list[ApplicationResult] = []
        for match in matches:
            if not match.is_recommended:
                continue
            result = self.application_service.apply_to_job(match.job, profile)
            applications.append(result)

        return AutomationReport(matched_jobs=matches, applications=applications)

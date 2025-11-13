"""Data models used across the job search automation application."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Iterable, Optional


@dataclass(slots=True)
class Resume:
    """Represents the parsed resume content."""

    raw_text: str
    sections: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class JobPosting:
    """Represents a job listing fetched from a provider."""

    title: str
    company: str
    description: str
    url: str
    location: Optional[str] = None
    salary: Optional[str] = None
    source: Optional[str] = None
    posted_at: Optional[datetime] = None


@dataclass(slots=True)
class MatchingResult:
    """Outcome of matching a job posting to the resume."""

    job: JobPosting
    similarity: float
    llm_reasoning: Optional[str] = None
    is_recommended: bool = False


@dataclass(slots=True)
class ApplicationResult:
    """Represents the result of attempting to apply to a job."""

    job: JobPosting
    applied: bool
    message: Optional[str] = None


@dataclass(slots=True)
class CandidateProfile:
    """Structured data extracted from the resume for applications."""

    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: Iterable[str] = field(default_factory=tuple)
    experience_summary: Optional[str] = None
    education_summary: Optional[str] = None

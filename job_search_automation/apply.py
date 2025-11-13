"""Services to automate job applications."""
from __future__ import annotations

from dataclasses import dataclass

from .models import ApplicationResult, CandidateProfile, JobPosting

try:  # pragma: no cover - optional dependency
    import requests
except Exception:  # pragma: no cover - library optional
    requests = None  # type: ignore


@dataclass(slots=True)
class JobApplicationService:
    """Automates applying to job postings via HTTP endpoints."""

    application_webhook: str | None = None

    def apply_to_job(self, job: JobPosting, profile: CandidateProfile) -> ApplicationResult:
        if not job.url:
            return ApplicationResult(job=job, applied=False, message="Job listing is missing an application URL")

        if not self.application_webhook:
            return ApplicationResult(
                job=job,
                applied=False,
                message=(
                    "No application webhook configured. Provide one to enable automated submissions."
                ),
            )

        payload = {
            "job_title": job.title,
            "company": job.company,
            "job_url": job.url,
            "candidate": {
                "name": profile.name,
                "email": profile.email,
                "phone": profile.phone,
                "skills": list(profile.skills),
                "experience_summary": profile.experience_summary,
                "education_summary": profile.education_summary,
            },
        }

        if requests is None:
            return ApplicationResult(
                job=job,
                applied=False,
                message=(
                    "The 'requests' package is not installed. Install it to enable automated submissions."
                ),
            )

        try:
            response = requests.post(self.application_webhook, json=payload, timeout=20)
            response.raise_for_status()
        except requests.RequestException as exc:  # type: ignore[attr-defined]
            return ApplicationResult(job=job, applied=False, message=str(exc))

        return ApplicationResult(job=job, applied=True, message="Application submitted")

"""Command line interface for the job search automation pipeline."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .apply import JobApplicationService
from .automation import JobSearchAutomator
from .config import AutomationConfig, JobSearchConfig, LLMConfig, ResumeConfig
from .job_fetchers.base import StaticJobFetcher
from .job_fetchers.serpapi import SerpApiJobFetcher
from .llm import LLMClient
from .matcher import JobMatcher
from .models import JobPosting
from .resume_parser import ResumeParser
from .retriever import ResumeRetriever


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Automate job search and applications with RAG.")
    parser.add_argument("resume", type=Path, help="Path to the resume file (txt or pdf)")
    parser.add_argument("keywords", nargs="+", help="Keywords to search for")
    parser.add_argument("--location", help="Location filter for job search")
    parser.add_argument("--provider", default="serpapi", help="Job provider (serpapi or static)")
    parser.add_argument("--max-results", type=int, default=20)
    parser.add_argument("--webhook", help="Webhook URL to submit applications to")
    parser.add_argument("--llm-model", default="gpt-4o-mini")
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--resume-chunk", type=int, default=400)
    parser.add_argument("--resume-overlap", type=int, default=50)
    parser.add_argument("--static-jobs", help="Path to a JSON file with static job postings for testing")
    return parser


def load_static_jobs(path: Path) -> list[JobPosting]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    jobs: list[JobPosting] = []
    for item in payload:
        jobs.append(
            JobPosting(
                title=item["title"],
                company=item.get("company", ""),
                description=item.get("description", ""),
                url=item.get("url", ""),
                location=item.get("location"),
                salary=item.get("salary"),
                source=item.get("source"),
            )
        )
    return jobs


def main(argv: list[str] | None = None) -> None:
    parser = build_argument_parser()
    args = parser.parse_args(argv)

    resume_config = ResumeConfig(path=args.resume, chunk_size=args.resume_chunk, chunk_overlap=args.resume_overlap)
    job_search_config = JobSearchConfig(
        provider=args.provider,
        keywords=args.keywords,
        location=args.location,
        max_results=args.max_results,
    )
    llm_config = LLMConfig(model=args.llm_model, temperature=args.temperature)
    config = AutomationConfig(resume=resume_config, job_search=job_search_config, llm=llm_config)

    resume_parser = ResumeParser()
    retriever = ResumeRetriever()
    llm_client = LLMClient(llm_config)
    matcher = JobMatcher(retriever, llm_client)
    application_service = JobApplicationService(application_webhook=args.webhook)

    if args.provider == "serpapi":
        job_fetcher = SerpApiJobFetcher(job_search_config)
    elif args.provider == "static":
        if not args.static_jobs:
            parser.error("--static-jobs must be provided when using the static provider")
        job_fetcher = StaticJobFetcher(load_static_jobs(Path(args.static_jobs)))
    else:
        parser.error(f"Unsupported job provider '{args.provider}'")

    automator = JobSearchAutomator(
        config=config,
        resume_parser=resume_parser,
        job_fetcher=job_fetcher,
        matcher=matcher,
        application_service=application_service,
    )
    report = automator.run()

    for match in report.matched_jobs:
        print(f"Job: {match.job.title} at {match.job.company}")
        print(f"Similarity: {match.similarity:.2f}")
        print(f"Recommended: {'Yes' if match.is_recommended else 'No'}")
        if match.llm_reasoning:
            print("Reasoning:\n" + match.llm_reasoning)
        print("-" * 60)

    for application in report.applications:
        status = "Submitted" if application.applied else "Skipped"
        print(f"Application {status} for {application.job.title} at {application.job.company}: {application.message}")


if __name__ == "__main__":  # pragma: no cover
    main()

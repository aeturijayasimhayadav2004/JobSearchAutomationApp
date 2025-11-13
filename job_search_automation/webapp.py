"""Flask web application that wraps the job matching pipeline."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from flask import Flask, flash, render_template, request

from .config import JobSearchConfig, LLMConfig
from .job_fetchers.local import LocalJobFetcher
from .llm import LLMClient
from .matcher import JobMatcher, MatchSettings
from .models import MatchingResult, Resume
from .retriever import ResumeRetriever


@dataclass(slots=True)
class FormData:
    resume_text: str
    keywords: list[str]
    location: str | None


def create_app(template_folder: str | None = None) -> Flask:
    """Create and configure the Flask application."""

    template_dir = template_folder or str(Path(__file__).resolve().parent / "templates")
    app = Flask(__name__, template_folder=template_dir)
    app.config.setdefault("SECRET_KEY", "dev")

    @app.route("/", methods=["GET", "POST"])
    def index() -> str:
        if request.method == "POST":
            form = _parse_form()
            if not form.resume_text.strip():
                flash("Please paste your resume text so we can evaluate matches.", "error")
                return render_template("index.html", results=None, form=form)

            matches = _run_matching_pipeline(form)
            if not matches:
                flash("No jobs matched the provided keywords. Try broadening your search.", "info")

            return render_template("index.html", results=matches, form=form)

        return render_template("index.html", results=None, form=FormData("", [], None))

    def _parse_form() -> FormData:
        resume_text = request.form.get("resume_text", "")
        keywords_raw = request.form.get("keywords", "")
        location = request.form.get("location") or None
        keywords = [word.strip() for word in keywords_raw.split(",") if word.strip()]
        return FormData(resume_text=resume_text, keywords=keywords, location=location)

    def _run_matching_pipeline(form: FormData) -> Sequence[MatchingResult]:
        resume = Resume(raw_text=form.resume_text, sections={"summary": form.resume_text})

        retriever = ResumeRetriever(max_snippets=3)
        retriever.index(resume, chunk_size=200, overlap=40)

        llm_client = LLMClient(LLMConfig(provider="offline"))
        matcher = JobMatcher(retriever=retriever, llm_client=llm_client, settings=MatchSettings(similarity_threshold=0.2))

        job_config = JobSearchConfig(
            provider="local",
            keywords=form.keywords or form.resume_text.split()[:8],
            location=form.location,
            max_results=25,
        )
        fetcher = LocalJobFetcher(job_config)
        jobs = list(fetcher.search())

        return matcher.score_jobs(jobs)

    @app.route("/health", methods=["GET"])
    def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    return app


__all__ = ["create_app"]

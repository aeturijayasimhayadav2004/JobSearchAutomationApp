"""Logic for matching job postings to the candidate's resume."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from .llm import LLMClient
from .models import JobPosting, MatchingResult, Resume
from .retriever import ResumeRetriever


@dataclass(slots=True)
class MatchSettings:
    similarity_threshold: float = 0.25
    top_k_snippets: int = 3


class JobMatcher:
    """Coordinates the retrieval and LLM reasoning to score jobs."""

    def __init__(self, retriever: ResumeRetriever, llm_client: LLMClient, settings: MatchSettings | None = None) -> None:
        self.retriever = retriever
        self.llm_client = llm_client
        self.settings = settings or MatchSettings()

    def prepare(self, resume: Resume, chunk_size: int, overlap: int) -> None:
        self.retriever.index(resume, chunk_size=chunk_size, overlap=overlap)

    def score_jobs(self, jobs: Iterable[JobPosting]) -> Sequence[MatchingResult]:
        results: list[MatchingResult] = []
        for job in jobs:
            contexts = self.retriever.query(job, top_k=self.settings.top_k_snippets)
            if not contexts:
                continue
            similarity = max(context.score for context in contexts)
            reasoning = self.llm_client.generate_match_analysis(
                job_title=job.title,
                job_description=job.description,
                resume_snippets=[context.snippet for context in contexts],
                similarity_score=similarity,
            )
            is_recommended = similarity >= self.settings.similarity_threshold and "yes" in reasoning.lower()
            results.append(
                MatchingResult(
                    job=job,
                    similarity=similarity,
                    llm_reasoning=reasoning,
                    is_recommended=is_recommended,
                )
            )
        return results

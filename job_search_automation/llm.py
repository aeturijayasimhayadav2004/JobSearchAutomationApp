"""LLM integration utilities."""
from __future__ import annotations

import os
from typing import Iterable

from .config import LLMConfig

try:  # pragma: no cover - optional dependency
    import openai
except Exception:  # pragma: no cover - library optional
    openai = None  # type: ignore


class LLMClient:
    """Minimal client for calling an LLM provider."""

    def __init__(self, config: LLMConfig) -> None:
        self.config = config

    def _ensure_openai(self) -> None:
        if openai is None:
            raise RuntimeError(
                "The 'openai' package is required for the configured provider. Install it via 'pip install openai'."
            )

        api_key = os.getenv(self.config.api_key_env)
        if not api_key:
            raise RuntimeError(
                f"Missing OpenAI API key. Set the {self.config.api_key_env} environment variable."
            )
        openai.api_key = api_key

    def generate_match_analysis(
        self,
        job_title: str,
        job_description: str,
        resume_snippets: Iterable[str],
        similarity_score: float,
    ) -> str:
        """Use the LLM to produce a reasoning summary for the match."""

        if self.config.provider != "openai":
            return self._fallback_analysis(
                job_title=job_title,
                job_description=job_description,
                resume_snippets=resume_snippets,
                similarity_score=similarity_score,
            )

        try:
            self._ensure_openai()
        except RuntimeError:
            # The OpenAI dependency is optional for local demos. Falling back to
            # a deterministic heuristic keeps the rest of the pipeline working
            # without network access or extra packages installed.
            return self._fallback_analysis(
                job_title=job_title,
                job_description=job_description,
                resume_snippets=resume_snippets,
                similarity_score=similarity_score,
            )

        prompt = self._build_prompt(job_title, job_description, resume_snippets, similarity_score)

        completion = openai.ChatCompletion.create(  # type: ignore[attr-defined]
            model=self.config.model,
            messages=[
                {"role": "system", "content": "You are an assistant that evaluates job fit."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
        )
        return completion["choices"][0]["message"]["content"].strip()

    def _build_prompt(
        self,
        job_title: str,
        job_description: str,
        resume_snippets: Iterable[str],
        similarity_score: float,
    ) -> str:
        context = "\n---\n".join(resume_snippets)
        return (
            "Evaluate whether the candidate is a strong fit for the job.\n"
            f"Job Title: {job_title}\n"
            f"Job Description:\n{job_description}\n\n"
            f"Similarity score from retrieval model: {similarity_score:.3f}.\n"
            "Relevant resume snippets:\n"
            f"{context}\n\n"
            "Respond with a concise summary highlighting strengths, gaps, and a final yes/no recommendation."
        )

    def _fallback_analysis(
        self,
        job_title: str,
        job_description: str,
        resume_snippets: Iterable[str],
        similarity_score: float,
    ) -> str:
        """Produce a deterministic summary when the OpenAI client is unavailable."""

        snippet_preview = " ".join(list(resume_snippets)[:1])[:240]
        description_focus = job_description.split(". ")[0][:240]

        if similarity_score >= 0.4:
            verdict = "YES"
            takeaway = "The resume strongly aligns with the job requirements."
        elif similarity_score >= 0.25:
            verdict = "YES"
            takeaway = "The match looks promising with some gaps to address."
        else:
            verdict = "NO"
            takeaway = "The overlap with the resume is limited."

        return (
            f"Role: {job_title}. First job detail: {description_focus}. "
            f"Resume highlight: {snippet_preview}. {takeaway} Recommendation: {verdict}."
        )

"""Utilities for loading and parsing resumes."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

from .models import CandidateProfile, Resume


class ResumeParserError(RuntimeError):
    """Raised when the resume cannot be loaded or parsed."""


class ResumeParser:
    """Parses resume files into structured data used across the pipeline."""

    def __init__(self, stopwords: Iterable[str] | None = None) -> None:
        self.stopwords = set(stopwords or [])

    def load(self, path: Path) -> Resume:
        """Load the resume file into memory."""

        if not path.exists():
            raise ResumeParserError(f"Resume file not found: {path}")

        if path.suffix.lower() in {".txt", ".md"}:
            text = path.read_text(encoding="utf-8")
        elif path.suffix.lower() == ".pdf":
            text = self._load_pdf(path)
        else:
            raise ResumeParserError(
                f"Unsupported resume format '{path.suffix}'. Provide TXT, MD, or PDF."
            )

        cleaned = "\n".join(line.strip() for line in text.splitlines() if line.strip())
        sections = self._split_sections(cleaned)
        return Resume(raw_text=cleaned, sections=sections)

    def extract_profile(self, resume: Resume) -> CandidateProfile:
        """Extract a lightweight profile from the resume sections."""

        header = resume.sections.get("summary") or resume.sections.get("experience")
        skills = resume.sections.get("skills", "")
        skills_list = [skill.strip() for skill in skills.split(",") if skill.strip()]

        return CandidateProfile(
            experience_summary=header,
            skills=skills_list,
        )

    def _split_sections(self, text: str) -> dict[str, str]:
        sections: dict[str, str] = {}
        current_section = "summary"
        buffer: list[str] = []

        for line in text.splitlines():
            normalized = line.lower().strip().strip(":")
            if len(normalized) < 60 and normalized.isalpha():
                if buffer:
                    sections[current_section] = "\n".join(buffer).strip()
                current_section = normalized
                buffer = []
            else:
                buffer.append(line)

        if buffer:
            sections[current_section] = "\n".join(buffer).strip()

        return sections

    def _load_pdf(self, path: Path) -> str:
        try:
            from pdfminer.high_level import extract_text  # type: ignore
        except ImportError as exc:  # pragma: no cover - library optional
            raise ResumeParserError(
                "pdfminer.six is required to parse PDF resumes. Install it via 'pip install pdfminer.six'."
            ) from exc

        text = extract_text(path)
        if not text:
            raise ResumeParserError("No text could be extracted from the PDF resume.")
        return text

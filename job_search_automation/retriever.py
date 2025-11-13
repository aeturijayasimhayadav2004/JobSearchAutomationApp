"""Simple retrieval module that powers the RAG pipeline."""
from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from typing import Sequence

from .models import JobPosting, Resume


@dataclass(slots=True)
class RetrievedContext:
    """Container for retrieved resume snippets."""

    snippet: str
    score: float


class ResumeRetriever:
    """Retrieves the most relevant resume snippets for a job description."""

    def __init__(self, max_snippets: int = 3) -> None:
        self.max_snippets = max_snippets
        self._resume_chunks: list[str] = []
        self._resume_vectors: list[dict[str, float]] | None = None
        self._idf: dict[str, float] = {}

    def index(self, resume: Resume, chunk_size: int = 400, overlap: int = 50) -> None:
        """Chunk the resume and build an index."""

        self._resume_chunks = self._chunk_text(resume.raw_text, chunk_size, overlap)
        if not self._resume_chunks:
            raise ValueError("Resume did not produce any chunks for retrieval")

        tokenized_chunks = [self._tokenize(chunk) for chunk in self._resume_chunks]
        self._idf = self._compute_idf(tokenized_chunks)
        self._resume_vectors = [self._tfidf(tokens, self._idf) for tokens in tokenized_chunks]

    def query(self, job: JobPosting, top_k: int | None = None) -> Sequence[RetrievedContext]:
        """Return the top resume snippets relevant to the job description."""

        if self._resume_vectors is None:
            raise RuntimeError("Retriever has not been indexed. Call 'index' first.")

        query_tokens = self._tokenize(job.description)
        query_vector = self._tfidf(query_tokens, self._idf)
        similarities = [self._cosine_similarity(query_vector, vector) for vector in self._resume_vectors]
        top_k = top_k or self.max_snippets
        ranked = sorted(
            zip(self._resume_chunks, similarities), key=lambda item: item[1], reverse=True
        )[:top_k]
        return [RetrievedContext(snippet=text, score=float(score)) for text, score in ranked]

    def _chunk_text(self, text: str, chunk_size: int, overlap: int) -> list[str]:
        if chunk_size <= overlap:
            raise ValueError("chunk_size must be greater than overlap")

        words = text.split()
        chunks: list[str] = []
        start = 0
        while start < len(words):
            end = min(start + chunk_size, len(words))
            chunk = " ".join(words[start:end])
            chunks.append(chunk)
            if end == len(words):
                break
            start = max(0, end - overlap)
        return chunks

    def _tokenize(self, text: str) -> list[str]:
        return [token for token in re.findall(r"[a-zA-Z0-9]+", text.lower()) if token]

    def _compute_idf(self, documents: list[list[str]]) -> dict[str, float]:
        doc_count = len(documents)
        df: Counter[str] = Counter()
        for tokens in documents:
            df.update(set(tokens))
        return {
            term: math.log((1 + doc_count) / (1 + freq)) + 1.0 for term, freq in df.items()
        }

    def _tfidf(self, tokens: list[str], idf: dict[str, float]) -> dict[str, float]:
        counts = Counter(tokens)
        if not counts:
            return {}
        max_tf = max(counts.values())
        vector: dict[str, float] = {}
        for term, freq in counts.items():
            weight = (0.5 + 0.5 * (freq / max_tf)) * idf.get(term, 0.0)
            if weight:
                vector[term] = weight
        return vector

    def _cosine_similarity(self, vec_a: dict[str, float], vec_b: dict[str, float]) -> float:
        if not vec_a or not vec_b:
            return 0.0
        intersection = set(vec_a.keys()) & set(vec_b.keys())
        numerator = sum(vec_a[token] * vec_b[token] for token in intersection)
        denom_a = math.sqrt(sum(weight * weight for weight in vec_a.values()))
        denom_b = math.sqrt(sum(weight * weight for weight in vec_b.values()))
        if denom_a == 0 or denom_b == 0:
            return 0.0
        return numerator / (denom_a * denom_b)

# Job Search Automation App

This project provides a Retrieval Augmented Generation (RAG) workflow that searches for jobs, evaluates their fit against a candidate's resume, and now ships with a simple Flask interface for exploring matches in the browser.

## Features

- **Browser experience** powered by Flask that lets you paste resume text and instantly view recommended roles.
- **Retrieval augmented matching** that indexes the resume and identifies the most relevant snippets for each job posting using TF-IDF similarity.
- **LLM reasoning** with an offline-friendly heuristic fallback so the demo works without external APIs.
- **Job providers** including a bundled local dataset for offline demos plus the SerpAPI-powered Google Jobs fetcher.
- **Automated applications** via configurable webhook submissions (optional for advanced workflows).

## Getting Started

1. Install dependencies:

   ```bash
   pip install -e .
   ```

2. (Optional) Export API keys if you plan to call OpenAI or SerpAPI directly:

   ```bash
   export OPENAI_API_KEY="sk-your-key"          # enables OpenAI reasoning
   export SERPAPI_API_KEY="serpapi-key"         # enables live Google Jobs search
   ```

3. Launch the Flask web application:

   ```bash
   flask --app job_search_automation.webapp:create_app run --reload
   ```

   Then open <http://127.0.0.1:5000> and paste your resume text plus optional keywords/location filters. The bundled dataset provides a curated set of Python-focused roles so the demo works fully offline.

4. Prefer the original CLI workflow? Prepare a resume file (TXT, Markdown, or PDF) and run:

   ```bash
   python -m job_search_automation.cli resume.txt "machine learning" "python" --location "Remote" --webhook https://example.com/apply
   ```

   Use `--provider static --static-jobs jobs.json` to test with offline job data.

## Running Tests

```bash
pytest
```

## Architecture Overview

The automation pipeline is composed of modular components:

- `ResumeParser` loads the resume and extracts structured sections.
- `ResumeRetriever` builds a TF-IDF vector store of resume chunks to provide grounding context.
- `JobMatcher` uses the retriever and `LLMClient` to score job listings and request match reasoning from an LLM.
- `JobApplicationService` submits recommended jobs to a webhook for automated applications.
- `JobSearchAutomator` orchestrates the full RAG loop end-to-end.

Refer to [`job_search_automation/cli.py`](job_search_automation/cli.py) for a complete example of wiring the components together.

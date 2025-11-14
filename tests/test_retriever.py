from job_search_automation.models import JobPosting, Resume
from job_search_automation.retriever import ResumeRetriever


def test_resume_retriever_returns_ranked_snippets():
    resume = Resume(
        raw_text=(
            "Python developer with experience in machine learning and data engineering. "
            "Built scalable pipelines using AWS and Docker."
        )
    )
    retriever = ResumeRetriever(max_snippets=2)
    retriever.index(resume, chunk_size=10, overlap=2)

    job = JobPosting(
        title="Machine Learning Engineer",
        company="Tech Corp",
        description="Looking for a Python engineer with AWS experience to build data pipelines.",
        url="https://example.com",
    )
    contexts = retriever.query(job)

    assert len(contexts) == 2
    assert all(context.score >= 0 for context in contexts)
    assert any("Python" in context.snippet for context in contexts)

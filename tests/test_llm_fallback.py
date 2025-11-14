from job_search_automation.llm import LLMClient
from job_search_automation.config import LLMConfig


def test_offline_llm_fallback_includes_recommendation_keyword():
    client = LLMClient(LLMConfig(provider="offline"))
    reasoning = client.generate_match_analysis(
        job_title="Python Engineer",
        job_description="Build APIs in Flask.",
        resume_snippets=["Experienced Python developer with Flask background."],
        similarity_score=0.3,
    )

    assert "recommendation" in reasoning.lower()
    assert "yes" in reasoning.lower()

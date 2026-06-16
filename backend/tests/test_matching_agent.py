from app.services.agents.matching_agent import MatchingAgent


class DummyResume:
    raw_text = "Python FastAPI React PostgreSQL RAG LLM"


class DummyJob:
    parsed_jd_json = {"required_skills": ["Python", "FastAPI", "Kubernetes"]}


def test_matching_agent_scores_and_reports_missing_skills():
    result = MatchingAgent().score(DummyResume(), DummyJob())

    assert result["score"] > 0
    assert "Python" in result["matched_skills"]
    assert "Kubernetes" in result["missing_skills"]


from io import BytesIO

from docx import Document
from fastapi.testclient import TestClient


def make_resume() -> BytesIO:
    document = Document()
    document.add_heading("Taylor Candidate", level=1)
    document.add_paragraph(
        "Backend engineer with Python, FastAPI, React, PostgreSQL, Docker, RAG, and ChromaDB experience."
    )
    content = BytesIO()
    document.save(content)
    content.seek(0)
    return content


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_complete_application_workflow_requires_user_confirmation(client: TestClient) -> None:
    upload = client.post(
        "/resumes/upload",
        files={
            "file": (
                "taylor-resume.docx",
                make_resume(),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )
    assert upload.status_code == 200, upload.text
    resume = upload.json()
    assert resume["file_name"] == "taylor-resume.docx"

    imported = client.post(
        "/jobs/import-text",
        json={
            "company": "Example Labs",
            "title": "Backend Engineer",
            "location": "London",
            "url": "https://example.com/jobs/backend-engineer",
            "raw_description": (
                "We require Python, FastAPI, React, PostgreSQL, Docker, RAG, and ChromaDB skills. "
                "Build reliable APIs and collaborate across the full product lifecycle."
            ),
        },
    )
    assert imported.status_code == 200, imported.text
    job = imported.json()

    matched = client.post(f"/jobs/{job['id']}/match/{resume['id']}")
    assert matched.status_code == 200, matched.text
    match_payload = matched.json()
    assert match_payload["match"]["score"] >= 70
    application_id = match_payload["application_id"]

    pending = client.get("/applications/pending")
    assert pending.status_code == 200
    assert [item["id"] for item in pending.json()] == [application_id]
    assert pending.json()[0]["confirmed_by_user"] is False

    detail = client.get(f"/applications/{application_id}")
    assert detail.status_code == 200
    assert detail.json()["job"]["company"] == "Example Labs"
    assert detail.json()["materials"][0]["material_type"] == "cover_letter"

    material = detail.json()["materials"][0]
    updated = client.put(
        f"/materials/{material['id']}",
        json={"content": "Reviewed and tailored cover letter."},
    )
    assert updated.status_code == 200
    assert updated.json()["content"] == "Reviewed and tailored cover letter."

    confirmed = client.post(f"/applications/{application_id}/confirm")
    assert confirmed.status_code == 200
    assert confirmed.json()["status"] == "applied"
    assert confirmed.json()["confirmed_by_user"] is True

    assert client.get("/applications/pending").json() == []
    duplicate_confirmation = client.post(f"/applications/{application_id}/confirm")
    assert duplicate_confirmation.status_code == 409


def test_match_rejects_unknown_resources(client: TestClient) -> None:
    response = client.post(
        "/jobs/00000000-0000-0000-0000-000000000000/match/00000000-0000-0000-0000-000000000000"
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Job or resume not found."

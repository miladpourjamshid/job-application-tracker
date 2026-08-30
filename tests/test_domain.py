from datetime import UTC, datetime, timedelta


def test_company_contact_and_interview_flow(client):
    company = client.post(
        "/companies",
        json={
            "name": "Acme Corp",
            "website": "https://acme.example",
            "industry": "Technology",
        },
    )
    assert company.status_code == 201
    company_id = company.json()["id"]

    assert client.get("/companies").status_code == 200
    assert client.get(f"/companies/{company_id}").status_code == 200

    contact = client.post(
        f"/companies/{company_id}/contacts",
        json={
            "name": "Jane Recruiter",
            "role": "Recruiter",
            "email": "jane@acme.example",
            "linkedin_url": "https://linkedin.com/in/jane-recruiter",
        },
    )
    assert contact.status_code == 201
    contact_id = contact.json()["id"]

    application = client.post(
        "/applications",
        json={
            "company": "Acme Corp",
            "company_id": company_id,
            "role": "Backend Intern",
        },
    )
    assert application.status_code == 201
    application_id = application.json()["id"]
    assert application.json()["company_id"] == company_id

    interview = client.post(
        f"/applications/{application_id}/interviews",
        json={
            "contact_id": contact_id,
            "interview_type": "technical",
            "scheduled_at": "2026-09-01T15:00:00Z",
            "notes": "Prepare Python and SQL questions.",
        },
    )
    assert interview.status_code == 201
    assert interview.json()["contact_id"] == contact_id

    interviews = client.get(f"/applications/{application_id}/interviews")
    assert interviews.status_code == 200
    assert len(interviews.json()) == 1

    contacts = client.get(f"/companies/{company_id}/contacts")
    assert contacts.status_code == 200
    assert contacts.json()[0]["name"] == "Jane Recruiter"


def test_duplicate_company_name_is_rejected(client):
    payload = {"name": "Acme Corp", "website": "https://acme.example"}
    first = client.post("/companies", json=payload)
    assert first.status_code == 201

    duplicate = client.post("/companies", json=payload)
    assert duplicate.status_code == 409


def test_application_history_records_status_changes(client):
    created = client.post(
        "/applications",
        json={"company": "History Co", "role": "Python Intern"},
    )
    application_id = created.json()["id"]

    history = client.get(f"/applications/{application_id}/history")
    assert history.status_code == 200
    assert history.json()[0]["status"] == "applied"

    updated = client.patch(
        f"/applications/{application_id}",
        json={"status": "interview"},
    )
    assert updated.status_code == 200

    history = client.get(f"/applications/{application_id}/history")
    assert [item["status"] for item in history.json()] == ["applied", "interview"]


def test_invalid_domain_references_return_404(client):
    contact = client.post(
        "/companies/99999/contacts",
        json={"name": "Nobody"},
    )
    assert contact.status_code == 404

    application = client.post(
        "/applications",
        json={
            "company": "Missing Co",
            "company_id": 99999,
            "role": "Developer",
        },
    )
    assert application.status_code == 404

    interview = client.post(
        "/applications/99999/interviews",
        json={
            "interview_type": "phone",
            "scheduled_at": datetime.now(UTC).isoformat(),
        },
    )
    assert interview.status_code == 404

    history = client.get("/applications/99999/history")
    assert history.status_code == 404


def test_interview_rejects_unknown_contact(client):
    application = client.post(
        "/applications",
        json={"company": "Interview Co", "role": "Developer"},
    )
    application_id = application.json()["id"]

    response = client.post(
        f"/applications/{application_id}/interviews",
        json={
            "contact_id": 99999,
            "interview_type": "video",
            "scheduled_at": (datetime.now(UTC) + timedelta(days=1)).isoformat(),
        },
    )
    assert response.status_code == 404

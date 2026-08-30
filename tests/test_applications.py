def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_and_get_application(client):
    payload = {
        "company": "OpenAI",
        "role": "Software Engineer Intern",
        "location": "Remote",
        "job_url": "https://example.com/jobs/123",
    }
    created = client.post("/applications", json=payload)
    assert created.status_code == 201
    data = created.json()
    assert data["company"] == "OpenAI"
    assert data["status"] == "applied"
    assert data["job_url"] == "https://example.com/jobs/123"

    fetched = client.get(f"/applications/{data['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["role"] == "Software Engineer Intern"


def test_filter_by_status_and_company(client):
    client.post("/applications", json={"company": "Acme", "role": "Python Intern"})
    client.post(
        "/applications",
        json={"company": "Beta", "role": "Backend Intern", "status": "interview"},
    )

    response = client.get("/applications?status=interview&company=beta")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["items"]) == 1
    assert payload["items"][0]["company"] == "Beta"


def test_update_and_delete_application(client):
    created = client.post(
        "/applications",
        json={"company": "Acme", "role": "Developer"},
    ).json()
    application_id = created["id"]

    updated = client.patch(
        f"/applications/{application_id}",
        json={"status": "interview", "notes": "Technical interview scheduled."},
    )
    assert updated.status_code == 200
    assert updated.json()["status"] == "interview"

    deleted = client.delete(f"/applications/{application_id}")
    assert deleted.status_code == 204
    assert client.get(f"/applications/{application_id}").status_code == 404


def test_missing_application_returns_404(client):
    response = client.get("/applications/9999")
    assert response.status_code == 404


def test_reject_invalid_deadline(client):
    response = client.post(
        "/applications",
        json={"company": "Acme", "role": "Developer", "deadline": "2026-01-01"},
    )
    assert response.status_code == 422

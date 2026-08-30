from datetime import UTC, datetime, timedelta


def test_dashboard_reports_only_current_users_data(client):
    first = client.post(
        "/applications",
        json={"company": "Acme", "role": "Engineer", "status": "applied"},
    )
    assert first.status_code == 201
    application_id = first.json()["id"]

    update = client.patch(
        f"/applications/{application_id}",
        json={"status": "offer"},
    )
    assert update.status_code == 200

    interview = client.post(
        f"/applications/{application_id}/interviews",
        json={
            "interview_type": "technical",
            "scheduled_at": (datetime.now(UTC) + timedelta(days=2)).isoformat(),
        },
    )
    assert interview.status_code == 201

    response = client.get("/dashboard")

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_applications"] == 1
    assert payload["by_status"]["offer"] == 1
    assert payload["offers"] == 1
    assert payload["rejections"] == 0
    assert payload["upcoming_interviews"] == 1
    assert payload["upcoming_deadlines"] == 0


def test_dashboard_requires_authentication(raw_client):
    response = raw_client.get("/dashboard")
    assert response.status_code == 401

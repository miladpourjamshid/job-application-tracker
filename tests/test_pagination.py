from datetime import date


def _application(company: str, role: str, applied_date: str) -> dict[str, str]:
    return {
        "company": company,
        "role": role,
        "applied_date": applied_date,
    }


def test_pagination_returns_metadata_and_items(client):
    for index in range(3):
        response = client.post(
            "/applications",
            json=_application(
                f"Company {index}",
                "Software Engineer",
                date(2026, 8, 1 + index).isoformat(),
            ),
        )
        assert response.status_code == 201

    response = client.get("/applications?page=2&page_size=2")

    assert response.status_code == 200
    payload = response.json()
    assert payload["page"] == 2
    assert payload["page_size"] == 2
    assert payload["total"] == 3
    assert payload["pages"] == 2
    assert len(payload["items"]) == 1


def test_pagination_can_filter_by_status(client):
    client.post("/applications", json=_application("Acme", "Engineer", "2026-08-01"))
    client.post("/applications", json=_application("Globex", "Engineer", "2026-08-02"))
    update = client.patch("/applications/1", json={"status": "interview"})
    assert update.status_code == 200

    response = client.get("/applications?status=interview&page=1&page_size=10")

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert payload["items"][0]["status"] == "interview"

def _register_and_login(client, email: str) -> dict[str, str]:
    registered = client.post(
        "/auth/register", json={"email": email, "password": "strong-password"}
    )
    assert registered.status_code == 201
    login = client.post(
        "/auth/login",
        data={"username": email, "password": "strong-password"},
    )
    assert login.status_code == 200
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def test_users_can_only_access_their_own_applications(raw_client):
    first_headers = _register_and_login(raw_client, "first@example.com")
    second_headers = _register_and_login(raw_client, "second@example.com")

    created = raw_client.post(
        "/applications",
        headers=first_headers,
        json={"company": "Private Co", "role": "Developer"},
    )
    assert created.status_code == 201
    application_id = created.json()["id"]

    own_list = raw_client.get("/applications", headers=first_headers)
    assert own_list.status_code == 200
    assert [item["id"] for item in own_list.json()["items"]] == [application_id]

    other_list = raw_client.get("/applications", headers=second_headers)
    assert other_list.status_code == 200
    assert other_list.json()["items"] == []

    assert raw_client.get(
        f"/applications/{application_id}", headers=second_headers
    ).status_code == 404
    assert raw_client.patch(
        f"/applications/{application_id}",
        headers=second_headers,
        json={"status": "interview"},
    ).status_code == 404
    assert raw_client.delete(
        f"/applications/{application_id}", headers=second_headers
    ).status_code == 404

    assert raw_client.get(
        f"/applications/{application_id}", headers=first_headers
    ).status_code == 200

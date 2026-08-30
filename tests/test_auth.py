def test_register_login_and_me(raw_client):
    registered = raw_client.post(
        "/auth/register",
        json={"email": "User@Example.com", "password": "strong-password"},
    )
    assert registered.status_code == 201
    assert registered.json()["email"] == "user@example.com"
    assert "password_hash" not in registered.json()

    duplicate = raw_client.post(
        "/auth/register",
        json={"email": "user@example.com", "password": "another-password"},
    )
    assert duplicate.status_code == 409

    login = raw_client.post(
        "/auth/login",
        data={"username": "user@example.com", "password": "strong-password"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    assert login.json()["token_type"] == "bearer"

    me = raw_client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == "user@example.com"


def test_login_rejects_bad_password(raw_client):
    raw_client.post(
        "/auth/register",
        json={"email": "login@example.com", "password": "strong-password"},
    )
    response = raw_client.post(
        "/auth/login",
        data={"username": "login@example.com", "password": "wrong-password"},
    )
    assert response.status_code == 401


def test_me_requires_valid_token(raw_client):
    response = raw_client.get("/auth/me")
    assert response.status_code == 401

    response = raw_client.get("/auth/me", headers={"Authorization": "Bearer invalid"})
    assert response.status_code == 401


def test_application_endpoints_require_authentication(raw_client):
    assert raw_client.get("/applications").status_code == 401
    response = raw_client.post(
        "/applications", json={"company": "Acme", "role": "Developer"}
    )
    assert response.status_code == 401

from fastapi.testclient import TestClient


def test_register_user(client: TestClient) -> None:
    payload = {
        "email": "user@example.com",
        "password": "secret123",
    }

    response = client.post("/register/", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == payload["email"]
    assert "id" in data
    assert "created_at" in data


def test_register_existing_email(client: TestClient) -> None:
    payload = {
        "email": "duplicate@example.com",
        "password": "secret123",
    }

    first = client.post("/register/", json=payload)
    assert first.status_code == 201

    second = client.post("/register/", json=payload)
    assert second.status_code == 400


def test_login_and_get_token(client: TestClient) -> None:
    email = "auth@example.com"
    password = "secret123"

    register_response = client.post(
        "/register/",
        json={"email": email, "password": password},
    )
    assert register_response.status_code == 201

    token_response = client.post(
        "/token/",
        data={
            "username": email,
            "password": password,
        },
    )

    assert token_response.status_code == 200
    token_data = token_response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"

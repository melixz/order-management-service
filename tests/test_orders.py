from fastapi.testclient import TestClient


def _register_and_login(client: TestClient) -> tuple[int, str]:
    email = "orders@example.com"
    password = "secret123"

    register_response = client.post(
        "/register/",
        json={"email": email, "password": password},
    )
    assert register_response.status_code == 201
    user = register_response.json()

    token_response = client.post(
        "/token/",
        data={
            "username": email,
            "password": password,
        },
    )
    assert token_response.status_code == 200
    token = token_response.json()["access_token"]

    return user["id"], token


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_create_and_get_order(client: TestClient) -> None:
    user_id, token = _register_and_login(client)

    order_payload = {
        "items": [
            {"product_id": 1, "quantity": 2, "price": 10.0},
            {"product_id": 2, "quantity": 1, "price": 5.0},
        ],
        "total_price": 25.0,
    }

    create_response = client.post(
        "/orders/",
        json=order_payload,
        headers=_auth_headers(token),
    )
    assert create_response.status_code == 201
    order = create_response.json()

    order_id = order["id"]

    get_response = client.get(
        f"/orders/{order_id}/",
        headers=_auth_headers(token),
    )
    assert get_response.status_code == 200
    fetched = get_response.json()

    assert fetched["id"] == order_id
    assert fetched["user_id"] == user_id
    assert fetched["total_price"] == order_payload["total_price"]
    assert len(fetched["items"]) == len(order_payload["items"])


def test_update_order_status(client: TestClient) -> None:
    _, token = _register_and_login(client)

    order_payload = {
        "items": [{"product_id": 1, "quantity": 1, "price": 10.0}],
        "total_price": 10.0,
    }

    create_response = client.post(
        "/orders/",
        json=order_payload,
        headers=_auth_headers(token),
    )
    assert create_response.status_code == 201
    order = create_response.json()
    order_id = order["id"]

    update_response = client.patch(
        f"/orders/{order_id}/",
        json={"status": "PAID"},
        headers=_auth_headers(token),
    )
    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["status"] == "PAID"


def test_get_user_orders(client: TestClient) -> None:
    user_id, token = _register_and_login(client)

    for _ in range(3):
        order_payload = {
            "items": [{"product_id": 1, "quantity": 1, "price": 10.0}],
            "total_price": 10.0,
        }
        response = client.post(
            "/orders/",
            json=order_payload,
            headers=_auth_headers(token),
        )
        assert response.status_code == 201

    list_response = client.get(
        f"/orders/user/{user_id}/",
        headers=_auth_headers(token),
    )
    assert list_response.status_code == 200
    orders = list_response.json()
    assert len(orders) == 3

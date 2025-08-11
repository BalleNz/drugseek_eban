import pytest


@pytest.mark.asyncio
async def test_auth_flow(test_user_data, client):
    # 1. Тест успешной аутентификации
    auth_response = client.post(
        "/v1/auth/",
        json=test_user_data
    )
    assert auth_response.status_code == 200
    auth_data = auth_response.json()
    assert "token" in auth_data
    assert isinstance(auth_data["token"], str)

    # 2. Тест получения данных пользователя с валидным токеном
    headers = {"Authorization": f"Bearer {auth_data['token']}"}
    user_response = client.get(
        "/v1/user/",
        headers=headers
    )
    assert user_response.status_code == 200
    user_data = user_response.json()
    assert user_data["telegram_id"] == test_user_data["telegram_id"]
    assert user_data["username"] == test_user_data["username"]

    # 3. Тест с невалидным токеном
    invalid_token_response = client.get(
        "/v1/user/",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert invalid_token_response.status_code == 401
    assert invalid_token_response.json()["detail"] == "JWT token invalid!"

    # 4. Тест с отсутствующим токеном
    no_token_response = client.get("/v1/user/")
    assert no_token_response.status_code == 401


@pytest.mark.asyncio
async def test_auth_invalid_data(client):
    # Тест с неполными данными
    incomplete_data = {
        "telegram_id": "123",
        "first_name": "Test"
    }
    response = client.post("/v1/auth/", json=incomplete_data)
    assert response.status_code == 422  # Ошибка валидации

    # Тест с пустыми данными
    empty_response = client.post("/v1/auth/", json={})
    assert empty_response.status_code == 422


@pytest.mark.asyncio
async def test_token_expiration(test_user_data, monkeypatch, client):
    # Меняем время жизни токена на 1 секунду для теста
    monkeypatch.setattr("config.config.ACCESS_TOKEN_EXPIRES_MINUTES", 0.0001)

    auth_response = client.post("/v1/auth/", json=test_user_data)
    token = auth_response.json()["token"]

    # Ждем немного, чтобы токен истек
    import time
    time.sleep(1)

    expired_response = client.get(
        "/v1/user/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert expired_response.status_code == 401
    assert expired_response.json()["detail"] == "JWT token expired!"
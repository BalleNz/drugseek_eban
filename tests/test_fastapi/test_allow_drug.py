import httpx
import pytest

from schemas import DrugSchema


@pytest.mark.asyncio
async def test_allow_drug(client, auth_token):
    "ТЕСТИРОВАНИЕ ПЕРЕДАЧИ ДОСТУПА ПРЕПАРАТА ЮЗЕРУ"
    paracetamol_id = "1c773dc0-2919-4671-aeca-439ab94c6f3a"

    headers = {"Authorization": f"Bearer {auth_token}"}

    async with httpx.AsyncClient(base_url="http://0.0.0.0:8000", timeout=None) as client:
        user_response = await client.get(f"/v1/user/", headers=headers)
        assert user_response.status_code == 200
        user_response_data = user_response.json()

        assert user_response_data
        user_tokens = user_response_data["allowed_requests"]

    async with httpx.AsyncClient(base_url="http://0.0.0.0:8000", timeout=None) as client:
        response = await client.post(f"/v1/drugs/allowed/{paracetamol_id}", headers=headers)
        assert response.status_code == 200

        response_data = response.json()
        assert response_data

    assert response_data['drug']
    assert response_data["is_allowed"] == True

    drug: DrugSchema = response_data['drug']

    async with httpx.AsyncClient(base_url="http://0.0.0.0:8000", timeout=None) as client:
        user_response = await client.get(f"/v1/user/", headers=headers)
        assert user_response.status_code == 200
        user_response_data = user_response.json()

        assert user_response_data
        user_new_tokens = int(user_response_data['allowed_requests'])

    assert drug["id"] in [data['drug_id'] for data in user_response_data["allowed_drugs"]]
    assert user_new_tokens == user_tokens  # не меняется тк уже был разрешен


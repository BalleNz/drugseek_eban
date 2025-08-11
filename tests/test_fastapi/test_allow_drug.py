import httpx
import pytest

from schemas import DrugSchema
from test_repository.test_drug_repo import create_test_drug_model


@pytest.mark.asyncio
async def test_allow_drug(client, user_service, drug_repo, auth_token):
    "ТЕСТИРОВАНИЕ ПЕРЕДАЧИ ДОСТУПА ПРЕПАРАТА ЮЗЕРУ"
    test_drug = create_test_drug_model()
    await drug_repo.create(test_drug)

    headers = {"Authorization": f"Bearer {auth_token}"}

    async with httpx.AsyncClient(base_url="http://0.0.0.0:8000", timeout=None) as client:
        response = await client.post(f"/v1/drugs/allow/{test_drug.id}", headers=headers)
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

    assert drug["id"] in [data['drug_id'] for data in user_response_data["allowed_drugs"]]
    assert user_response_data['allowed_requests'] == 2


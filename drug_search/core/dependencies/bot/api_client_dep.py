from drug_search.bot.api_client.drug_search_api import DrugSearchAPIClient
from drug_search.config import config

API_BASE_URL = config.WEBHOOK_URL
client = DrugSearchAPIClient(base_url=API_BASE_URL)


def get_api_client() -> DrugSearchAPIClient:
    """Singleton"""
    return client

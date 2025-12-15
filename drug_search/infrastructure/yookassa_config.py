import json
import logging

logger = logging.getLogger(__name__)

class YookassaConfig:

    @staticmethod
    def get_provider_data(
            description: str,  # Описание платежа
            price: float,  # Сумма платежа
            currency: str = "RUB"  # Валюта
    ) -> str:
        """Возвращает данные для чека в JSON

        Args:
            description (str): Описание платежа
            price (float): Цена в рублях
        """
        provider_data = {
            "receipt": {
                "items": [
                    {
                        "description": description,
                        "quantity": "1",
                        "amount": {
                            # Здесь цена уже в рублях, с двумя знаками
                            "value": f"{price:.2f}",
                            "currency": currency
                        },
                        "vat_code": 1  # Для самозанятых
                    }
                ]
            }
        }

        logging.info(f"Новый чек, цена: {price:.2f}")
        return json.dumps(provider_data)

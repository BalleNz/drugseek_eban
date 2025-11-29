import json

from aiogram import F
from fastapi import APIRouter

yookassa_router = APIRouter(prefix="/yookassa")


# Webhook endpoint (нужно настроить в админке Юкассы)
@yookassa_router.message(F.content_type == ContentType.WEB_APP_DATA)
async def handle_yookassa_webhook(message: Message):
    """Обработка webhook от Юкассы"""
    try:
        data = json.loads(message.web_app_data.data)
        payment_id = data.get('object', {}).get('id')

        if payment_id:
            payment = Payment.find_one(payment_id)

            if payment.status == "succeeded":
                user_id = payment.metadata.get('user_id')
                # Обработать успешный платеж
                # TODO: enqueue_yookassa_update_to_admins
                ...

    except Exception as e:
        print(f"Webhook error: {e}")

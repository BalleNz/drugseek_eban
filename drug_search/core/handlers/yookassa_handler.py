import json

from aiogram import F

router = Router


# Webhook endpoint (нужно настроить в админке Юкассы)
@payment_router.message(F.content_type == ContentType.WEB_APP_DATA)
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
                await handle_successful_payment(user_id, payment)

    except Exception as e:
        print(f"Webhook error: {e}")


async def handle_successful_payment(user_id: int, payment):
    """Обработка успешного платежа"""
    # Здесь можно отправить уведомление пользователю
    # или обновить статус в БД

    # Пример отправки уведомления
    from aiogram import Bot
    bot = Bot.get_current()
    try:
        await bot.send_message(
            user_id,
            "✅ Ваш платеж успешно обработан! Спасибо за покупку!"
        )
    except:
        pass  # Пользователь мог заблокировать бота
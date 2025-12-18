from aiogram.types import LabeledPrice, CallbackQuery

from drug_search.config import config
from drug_search.infrastructure.yookassa_config import YookassaConfig


async def send_invoice(
        callback_query: CallbackQuery,
        price: int,
        payment_description: str,
        package_key: str,

):
    """Выставление счёта пользователю (invoice)

    Args:
        price (int): Сумма платежа в рублях
        payment_description (str): Описание платежа
        package_key (str): Ключ пакета (подписки / токенов / ...)
        callback_query
    """

    prices = [
        LabeledPrice(
            label='Оплата заказа',
            amount=price * 100  # сумма платежа в копейках
        )
    ]

    title: str = ""
    match package_key.split("_")[0]:
        case "sub":
            title = "Оплата подписки"
        case "tokens":
            title = "Оплата пакета токенов"

    await callback_query.message.answer_invoice(
        title=title,
        description=f'{payment_description}',
        payload=f"{package_key}-{callback_query.from_user.id}",  # payload
        provider_token=config.PROVIDER_TOKEN,  # Токен из BotFather
        currency=config.CURRENCY,
        prices=prices,
        need_email=True,
        send_email_to_provider=True,
        need_phone_number=True,  # Для отправки чека
        send_phone_number_to_provider=True,
        provider_data=YookassaConfig.get_provider_data(
            description=payment_description,
            price=price
        )  # Данные для чека
    )

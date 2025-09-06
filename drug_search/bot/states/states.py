from aiogram.fsm.state import State, StatesGroup


class States(StatesGroup):
    # Drugs
    DRUG_DATABASE_MENU = State()  # База данных юзера
    DRUG_DATABASE_DESCRIBE = State()  # Описание препарата  (дозы, пути акт., комбинации, исследования)

    # User
    PROFILE = State()  # Профиль юзера

    # Payments
    PAYMENT = State()
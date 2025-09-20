from aiogram.fsm.state import State, StatesGroup


class States(StatesGroup):
    # Drugs
    DRUG_DATABASE_MENU = State()  # База данных юзера

    # User
    PROFILE = State()  # Профиль юзера

    # Payments
    PAYMENT = State()
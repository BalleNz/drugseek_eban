from aiogram.fsm.state import State, StatesGroup


class States(StatesGroup):
    # User
    PROFILE = State()  # Профиль юзера

    # Payments
    PAYMENT = State()

    # MAIN
    IN_PROCESS = State()

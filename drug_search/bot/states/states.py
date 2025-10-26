from aiogram.fsm.state import State, StatesGroup


class States(StatesGroup):
    # Payments
    PAYMENT = State()

    # MAIN
    IN_PROCESS = State()

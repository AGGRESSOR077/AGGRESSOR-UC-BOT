"""
AGGRESSOR UC BOT - Admin FSM holatlari.

Bu modul Broadcast xabar yozish va Sozlamalarni o'zgartirish
jarayonlarida ishlatiladigan holatlarni belgilaydi.
"""

from aiogram.fsm.state import State, StatesGroup


class BroadcastStates(StatesGroup):
    """
    Broadcast xabar yuborish jarayonidagi holatlar:

    1. waiting_for_message -> Yuboriladigan xabar matni kutilmoqda
    2. waiting_for_confirm -> Yuborishni tasdiqlash kutilmoqda
    """

    waiting_for_message = State()
    waiting_for_confirm = State()


class SettingsStates(StatesGroup):
    """
    Sozlamalarni o'zgartirish jarayonidagi holatlar:

    1. waiting_for_card_number -> Yangi karta raqami kutilmoqda
    2. waiting_for_card_owner  -> Yangi karta egasi ismi kutilmoqda
    """

    waiting_for_card_number = State()
    waiting_for_card_owner = State()

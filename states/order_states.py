"""
AGGRESSOR UC BOT - Buyurtma FSM holatlari.

Bu modul mijoz UC sotib olish jarayonida bosib o'tadigan
barcha bosqichlarni (state'larni) belgilaydi.
"""

from aiogram.fsm.state import State, StatesGroup


class OrderStates(StatesGroup):
    """
    Buyurtma yaratish jarayonidagi holatlar ketma-ketligi:

    1. waiting_for_uid   -> Mijoz PUBG UID kiritishi kutilmoqda
    2. waiting_for_receipt -> Mijoz to'lov chekini (rasm) yuborishi kutilmoqda
    """

    waiting_for_uid = State()
    waiting_for_receipt = State()

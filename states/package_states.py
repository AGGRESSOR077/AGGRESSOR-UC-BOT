"""
AGGRESSOR UC BOT - Paket boshqaruvi FSM holatlari.

Bu modul admin tomonidan paket qo'shish va tahrirlash
jarayonlarida ishlatiladigan holatlarni belgilaydi.
"""

from aiogram.fsm.state import State, StatesGroup


class PackageAddStates(StatesGroup):
    """
    Yangi paket qo'shish jarayonidagi holatlar ketma-ketligi:

    1. waiting_for_name      -> Paket nomi kutilmoqda
    2. waiting_for_uc_amount -> UC miqdori kutilmoqda
    3. waiting_for_price     -> Narx kutilmoqda
    """

    waiting_for_name = State()
    waiting_for_uc_amount = State()
    waiting_for_price = State()


class PackageEditStates(StatesGroup):
    """
    Mavjud paketni tahrirlash jarayonidagi holatlar:

    1. waiting_for_new_name      -> Yangi nom kutilmoqda
    2. waiting_for_new_uc_amount -> Yangi UC miqdori kutilmoqda
    3. waiting_for_new_price     -> Yangi narx kutilmoqda
    """

    waiting_for_new_name = State()
    waiting_for_new_uc_amount = State()
    waiting_for_new_price = State()

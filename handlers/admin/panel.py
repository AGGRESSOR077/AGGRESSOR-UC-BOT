"""
AGGRESSOR UC BOT - Admin panel handleri.

Bu modul /admin buyrug'ini, admin panel asosiy menyusini
va boshqa barcha admin handlerlarida ishlatiladigan
IsAdminFilter klassini o'z ichiga oladi.
"""

from aiogram import F, Router
from aiogram.filters import Command, Filter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, TelegramObject

from config import config
from keyboards.admin_kb import admin_panel_keyboard
from utils.texts import ADMIN_PANEL_MESSAGE, NOT_ADMIN_MESSAGE

router = Router(name="admin_panel")


class IsAdminFilter(Filter):
    """
    Foydalanuvchi admin ekanligini tekshiruvchi filter.

    Bu filter barcha admin handlerlarida ishlatiladi, shunda
    oddiy mijozlar admin funksiyalariga kira olmaydi.
    """

    async def __call__(self, event: TelegramObject) -> bool:
        user = event.from_user
        if user is None:
            return False
        return config.is_admin(user.id)


@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext) -> None:
    """
    /admin buyrug'i bosilganda ishga tushadi.

    Agar foydalanuvchi admin bo'lmasa, ruxsat yo'qligi haqida xabar beradi.
    Aks holda, admin panel asosiy menyusini ko'rsatadi.
    """
    if not config.is_admin(message.from_user.id):
        await message.answer(NOT_ADMIN_MESSAGE)
        return

    await state.clear()
    await message.answer(
        ADMIN_PANEL_MESSAGE,
        reply_markup=admin_panel_keyboard(),
    )


@router.callback_query(IsAdminFilter(), F.data == "back_to_admin_panel")
async def callback_back_to_admin_panel(callback: CallbackQuery, state: FSMContext) -> None:
    """Har qanday admin bo'limidan admin panelga qaytish uchun callback."""
    await state.clear()

    await callback.message.edit_text(
        ADMIN_PANEL_MESSAGE,
        reply_markup=admin_panel_keyboard(),
    )
    await callback.answer()

"""
AGGRESSOR UC BOT - Start handler.

Bu modul /start buyrug'ini va asosiy menyuga qaytish
callback'ini qayta ishlaydi.
"""

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database import db
from keyboards.user_kb import main_menu_keyboard
from utils.helpers import escape_html
from utils.texts import WELCOME_MESSAGE

router = Router(name="user_start")


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    """
    /start buyrug'i bosilganda ishga tushadi.

    Foydalanuvchini database'ga qo'shadi (agar mavjud bo'lmasa)
    va chiroyli Welcome Message bilan asosiy menyuni ko'rsatadi.
    """
    await state.clear()

    user = message.from_user
    await db.add_user(
        telegram_id=user.id,
        username=user.username,
        full_name=user.full_name,
    )

    full_name_safe = escape_html(user.full_name or "do'stim")

    await message.answer(
        WELCOME_MESSAGE.format(full_name=full_name_safe),
        reply_markup=main_menu_keyboard(),
    )


@router.callback_query(F.data == "back_to_main_menu")
async def callback_back_to_main_menu(callback: CallbackQuery, state: FSMContext) -> None:
    """Har qanday bo'limdan asosiy menyuga qaytish uchun callback."""
    await state.clear()

    user = callback.from_user
    full_name_safe = escape_html(user.full_name or "do'stim")

    await callback.message.edit_text(
        WELCOME_MESSAGE.format(full_name=full_name_safe),
        reply_markup=main_menu_keyboard(),
    )
    await callback.answer()

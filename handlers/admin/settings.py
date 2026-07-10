"""
AGGRESSOR UC BOT - Sozlamalar handleri.

Bu modul admin panelidagi "⚙ Sozlamalar" bo'limini boshqaradi:
to'lov uchun karta raqami va karta egasi ismini o'zgartirish.
"""

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from config import config
from database import db
from handlers.admin.panel import IsAdminFilter
from keyboards.admin_kb import cancel_action_keyboard, settings_menu_keyboard
from states.admin_states import SettingsStates
from utils.texts import (
    SETTINGS_CURRENT_CARD,
    SETTINGS_ENTER_CARD_NUMBER,
    SETTINGS_ENTER_CARD_OWNER,
    SETTINGS_MENU_MESSAGE,
    SETTINGS_UPDATED_SUCCESS,
)

router = Router(name="admin_settings")
router.message.filter(IsAdminFilter())
router.callback_query.filter(IsAdminFilter())


@router.callback_query(F.data == "admin_settings")
async def callback_admin_settings(callback: CallbackQuery) -> None:
    """"⚙ Sozlamalar" tugmasi bosilganda joriy karta ma'lumotlarini ko'rsatadi."""
    card_number = await db.get_setting("card_number", config.CARD_NUMBER)
    card_owner = await db.get_setting("card_owner", config.CARD_OWNER)

    text = SETTINGS_MENU_MESSAGE + "\n\n" + SETTINGS_CURRENT_CARD.format(
        card_number=card_number or "Kiritilmagan",
        card_owner=card_owner or "Kiritilmagan",
    )

    await callback.message.edit_text(
        text,
        reply_markup=settings_menu_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "settings_change_card_number")
async def callback_change_card_number(callback: CallbackQuery, state: FSMContext) -> None:
    """Karta raqamini o'zgartirish so'ralganda ishga tushadi."""
    await state.set_state(SettingsStates.waiting_for_card_number)
    await callback.message.edit_text(
        SETTINGS_ENTER_CARD_NUMBER,
        reply_markup=cancel_action_keyboard(),
    )
    await callback.answer()


@router.message(SettingsStates.waiting_for_card_number)
async def process_change_card_number(message: Message, state: FSMContext) -> None:
    """Yangi karta raqami kiritilganda database'ga saqlaydi."""
    new_card_number = message.text.strip()
    await db.set_setting("card_number", new_card_number)
    await state.clear()

    await message.answer(
        SETTINGS_UPDATED_SUCCESS,
        reply_markup=settings_menu_keyboard(),
    )


@router.callback_query(F.data == "settings_change_card_owner")
async def callback_change_card_owner(callback: CallbackQuery, state: FSMContext) -> None:
    """Karta egasi ismini o'zgartirish so'ralganda ishga tushadi."""
    await state.set_state(SettingsStates.waiting_for_card_owner)
    await callback.message.edit_text(
        SETTINGS_ENTER_CARD_OWNER,
        reply_markup=cancel_action_keyboard(),
    )
    await callback.answer()


@router.message(SettingsStates.waiting_for_card_owner)
async def process_change_card_owner(message: Message, state: FSMContext) -> None:
    """Yangi karta egasi ismi kiritilganda database'ga saqlaydi."""
    new_card_owner = message.text.strip()
    await db.set_setting("card_owner", new_card_owner)
    await state.clear()

    await message.answer(
        SETTINGS_UPDATED_SUCCESS,
        reply_markup=settings_menu_keyboard(),
    )

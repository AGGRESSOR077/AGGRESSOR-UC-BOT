"""
AGGRESSOR UC BOT - Broadcast handleri.

Bu modul admin panelidagi "📢 Broadcast" bo'limini boshqaradi:
admin xabar matnini kiritadi, tasdiqlaydi va bot barcha
foydalanuvchilarga xabarni yuboradi.
"""

import asyncio

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database import db
from handlers.admin.panel import IsAdminFilter
from keyboards.admin_kb import (
    admin_panel_keyboard,
    broadcast_confirm_keyboard,
    cancel_action_keyboard,
)
from states.admin_states import BroadcastStates
from utils.texts import (
    ADMIN_PANEL_MESSAGE,
    BROADCAST_CANCELLED,
    BROADCAST_CONFIRM,
    BROADCAST_ENTER_MESSAGE,
    BROADCAST_FINISHED,
    BROADCAST_STARTED,
)

router = Router(name="admin_broadcast")
router.message.filter(IsAdminFilter())
router.callback_query.filter(IsAdminFilter())


@router.callback_query(F.data == "admin_broadcast")
async def callback_admin_broadcast(callback: CallbackQuery, state: FSMContext) -> None:
    """"📢 Broadcast" tugmasi bosilganda xabar matnini so'raydi."""
    await state.set_state(BroadcastStates.waiting_for_message)
    await callback.message.edit_text(
        BROADCAST_ENTER_MESSAGE,
        reply_markup=cancel_action_keyboard(),
    )
    await callback.answer()


@router.message(Command("cancel"), BroadcastStates.waiting_for_message)
async def cmd_cancel_broadcast(message: Message, state: FSMContext) -> None:
    """/cancel buyrug'i orqali broadcast yozishni bekor qilish."""
    await state.clear()
    await message.answer(BROADCAST_CANCELLED, reply_markup=admin_panel_keyboard())


@router.message(BroadcastStates.waiting_for_message)
async def process_broadcast_message(message: Message, state: FSMContext) -> None:
    """Xabar matni kiritilganda, yuborishni tasdiqlashni so'raydi."""
    text = message.html_text or message.text or ""

    if not text.strip():
        await message.answer(
            "⚠ Iltimos, matnli xabar kiriting.",
            reply_markup=cancel_action_keyboard(),
        )
        return

    await state.update_data(broadcast_text=text)
    await state.set_state(BroadcastStates.waiting_for_confirm)

    user_count = await db.count_users()

    await message.answer(
        BROADCAST_CONFIRM.format(text=text, count=user_count),
        reply_markup=broadcast_confirm_keyboard(),
    )


@router.callback_query(BroadcastStates.waiting_for_confirm, F.data == "broadcast_confirm")
async def callback_broadcast_confirm(callback: CallbackQuery, state: FSMContext) -> None:
    """Admin yuborishni tasdiqlaganda, barcha foydalanuvchilarga xabar yuboradi."""
    data = await state.get_data()
    text = data.get("broadcast_text", "")

    await callback.message.edit_text(BROADCAST_STARTED)
    await callback.answer()

    telegram_ids = await db.get_all_user_telegram_ids(only_active=True)

    success_count = 0
    failed_count = 0

    for telegram_id in telegram_ids:
        try:
            await callback.bot.send_message(chat_id=telegram_id, text=text)
            success_count += 1
        except Exception:
            failed_count += 1

        # Telegram API rate limitiga tushib qolmaslik uchun kichik pauza
        await asyncio.sleep(0.05)

    await state.clear()

    await callback.message.answer(
        BROADCAST_FINISHED.format(success=success_count, failed=failed_count),
        reply_markup=admin_panel_keyboard(),
    )


@router.callback_query(BroadcastStates.waiting_for_confirm, F.data == "broadcast_cancel")
async def callback_broadcast_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    """Admin broadcast yuborishni bekor qilganda ishga tushadi."""
    await state.clear()
    await callback.message.edit_text(
        BROADCAST_CANCELLED,
        reply_markup=admin_panel_keyboard(),
    )
    await callback.answer()

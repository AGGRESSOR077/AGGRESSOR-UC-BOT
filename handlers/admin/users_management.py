# 📁 JOYLASHUV: aggressor_uc_bot/handlers/admin/users_management.py
# ⚠ YANGI FAYL
"""
AGGRESSOR UC BOT - Admin Foydalanuvchilar boshqaruvi handleri.
"""

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database import db
from handlers.admin.panel import IsAdminFilter
from keyboards.admin_kb import (
    back_to_admin_panel_keyboard,
    ban_reason_cancel_keyboard,
    user_profile_action_keyboard,
    users_pagination_keyboard,
)
from states.new_features_states import AdminMessageUserStates, BanStates
from utils.helpers import format_datetime_display, format_price
from utils.texts_new import (
    BAN_ENTER_REASON,
    BAN_SUCCESS_ADMIN,
    BAN_SUCCESS_USER,
    UNBAN_SUCCESS_ADMIN,
    UNBAN_SUCCESS_USER,
    USER_MESSAGE_ENTER_TEXT,
    USER_MESSAGE_RECEIVED_PREFIX,
    USER_MESSAGE_SENT_SUCCESS,
    USER_MESSAGE_SEND_FAILED,
    USER_PROFILE_MESSAGE,
    USERS_LIST_EMPTY,
    USERS_LIST_HEADER,
)

router = Router(name="admin_users_management")
router.message.filter(IsAdminFilter())
router.callback_query.filter(IsAdminFilter())

PAGE_SIZE = 10


async def _render_users_page(callback: CallbackQuery, page: int) -> None:
    total_pages = await db.get_users_total_pages(PAGE_SIZE)
    users = await db.get_users_paginated(page, PAGE_SIZE)

    if not users:
        await callback.message.edit_text(USERS_LIST_EMPTY, reply_markup=back_to_admin_panel_keyboard())
        return

    await callback.message.edit_text(
        USERS_LIST_HEADER.format(current_page=page, total_pages=total_pages),
        reply_markup=users_pagination_keyboard(users, page, total_pages),
    )


@router.callback_query(F.data == "admin_users")
async def callback_admin_users(callback: CallbackQuery) -> None:
    await _render_users_page(callback, page=1)
    await callback.answer()


@router.callback_query(F.data.startswith("users_page:"))
async def callback_users_page(callback: CallbackQuery) -> None:
    page = int(callback.data.split(":")[1])
    await _render_users_page(callback, page)
    await callback.answer()


@router.callback_query(F.data == "noop")
async def callback_noop(callback: CallbackQuery) -> None:
    await callback.answer()


@router.callback_query(F.data.startswith("view_user:"))
async def callback_view_user(callback: CallbackQuery) -> None:
    telegram_id = int(callback.data.split(":")[1])
    user = await db.get_user_by_telegram_id(telegram_id)

    if not user:
        await callback.answer("⚠ Foydalanuvchi topilmadi.", show_alert=True)
        return

    stats = await db.get_user_stats(telegram_id)
    status = "🚫 Ban qilingan" if user.is_banned else ("⛔ Bloklangan" if user.is_blocked else "✅ Faol")

    await callback.message.edit_text(
        USER_PROFILE_MESSAGE.format(
            full_name=user.full_name or "Noma'lum",
            username=user.username or "yo'q",
            telegram_id=user.telegram_id,
            orders_count=stats.orders_count,
            total_spent=stats.total_spent_display(),
            first_order=format_datetime_display(stats.first_order_at) if stats.first_order_at else "yo'q",
            last_order=format_datetime_display(stats.last_order_at) if stats.last_order_at else "yo'q",
            status=status,
        ),
        reply_markup=user_profile_action_keyboard(telegram_id, user.is_banned),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("view_user_orders:"))
async def callback_view_user_orders(callback: CallbackQuery) -> None:
    telegram_id = int(callback.data.split(":")[1])
    orders = await db.get_orders_by_user(telegram_id)

    if not orders:
        await callback.answer("📭 Bu foydalanuvchida buyurtmalar yo'q.", show_alert=True)
        return

    text = f"📦 <b>Foydalanuvchi buyurtmalari (ID: {telegram_id})</b>\n\n"
    for order in orders[:20]:
        text += f"{order.order_number} — {order.package_name} — {order.display_price()} — {order.status_display()}\n"

    await callback.message.edit_text(text, reply_markup=user_profile_action_keyboard(telegram_id, False))
    await callback.answer()


@router.callback_query(F.data.startswith("ban_user_start:"))
async def callback_ban_user_start(callback: CallbackQuery, state: FSMContext) -> None:
    telegram_id = int(callback.data.split(":")[1])
    await state.update_data(ban_telegram_id=telegram_id)
    await state.set_state(BanStates.waiting_for_reason)
    await callback.message.edit_text(BAN_ENTER_REASON, reply_markup=ban_reason_cancel_keyboard())
    await callback.answer()


@router.message(BanStates.waiting_for_reason)
async def process_ban_reason(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    telegram_id = data["ban_telegram_id"]
    reason = message.text.strip()

    await db.ban_user(telegram_id, reason)
    await db.add_admin_log(message.from_user.id, "ban_user", f"telegram_id={telegram_id}, reason={reason}")
    await state.clear()

    try:
        await message.bot.send_message(chat_id=telegram_id, text=BAN_SUCCESS_USER.format(reason=reason))
    except Exception:
        pass

    await message.answer(BAN_SUCCESS_ADMIN, reply_markup=back_to_admin_panel_keyboard())


@router.callback_query(F.data.startswith("unban_user:"))
async def callback_unban_user(callback: CallbackQuery) -> None:
    telegram_id = int(callback.data.split(":")[1])
    await db.unban_user(telegram_id)
    await db.add_admin_log(callback.from_user.id, "unban_user", f"telegram_id={telegram_id}")

    try:
        await callback.bot.send_message(chat_id=telegram_id, text=UNBAN_SUCCESS_USER)
    except Exception:
        pass

    await callback.message.edit_text(UNBAN_SUCCESS_ADMIN, reply_markup=back_to_admin_panel_keyboard())
    await callback.answer()


@router.callback_query(F.data.startswith("message_user:"))
async def callback_message_user_start(callback: CallbackQuery, state: FSMContext) -> None:
    telegram_id = int(callback.data.split(":")[1])
    await state.update_data(message_target_telegram_id=telegram_id)
    await state.set_state(AdminMessageUserStates.waiting_for_message)
    await callback.message.edit_text(USER_MESSAGE_ENTER_TEXT, reply_markup=ban_reason_cancel_keyboard())
    await callback.answer()


@router.message(AdminMessageUserStates.waiting_for_message)
async def process_message_user(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    telegram_id = data["message_target_telegram_id"]
    text = message.text.strip()
    await state.clear()

    try:
        await message.bot.send_message(
            chat_id=telegram_id,
            text=USER_MESSAGE_RECEIVED_PREFIX.format(text=text),
        )
        await db.add_admin_log(message.from_user.id, "message_user", f"telegram_id={telegram_id}")
        await message.answer(USER_MESSAGE_SENT_SUCCESS, reply_markup=back_to_admin_panel_keyboard())
    except Exception:
        await message.answer(USER_MESSAGE_SEND_FAILED, reply_markup=back_to_admin_panel_keyboard())

# 📁 JOYLASHUV: aggressor_uc_bot/handlers/admin/referral_settings.py
# ⚠ YANGI FAYL
"""
AGGRESSOR UC BOT - Admin Referral sozlamalari handleri.
"""

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database import db
from handlers.admin.panel import IsAdminFilter
from keyboards.admin_kb import (
    cancel_action_keyboard,
    referral_bonus_type_keyboard,
    referral_settings_keyboard,
)
from states.new_features_states import ReferralSettingsStates
from utils.helpers import format_price, is_valid_number, is_valid_price
from utils.texts_new import (
    REFERRAL_DISABLED,
    REFERRAL_ENABLED,
    REFERRAL_SETTINGS_ENTER_BONUS_VALUE,
    REFERRAL_SETTINGS_ENTER_MIN_ORDER,
    REFERRAL_SETTINGS_ENTER_THRESHOLD_COUNT,
    REFERRAL_SETTINGS_ENTER_THRESHOLD_PERCENT,
    REFERRAL_SETTINGS_MESSAGE,
    REFERRAL_SETTINGS_UPDATED,
)

router = Router(name="admin_referral_settings")
router.message.filter(IsAdminFilter())
router.callback_query.filter(IsAdminFilter())

BONUS_TYPE_DISPLAY = {
    "money": "💵 Pul",
    "discount": "🎫 Chegirma",
    "uc_discount": "🎮 UC narxiga chegirma",
}


async def _render_settings(callback: CallbackQuery) -> None:
    enabled = (await db.get_setting("referral_enabled", "1")) == "1"
    min_order = await db.get_setting("referral_min_order", "0")
    bonus_type = await db.get_setting("referral_bonus_type", "money")
    bonus_value = await db.get_setting("referral_bonus_value", "0")
    threshold_count = await db.get_setting("referral_threshold_count", "0")
    threshold_percent = await db.get_setting("referral_threshold_percent", "0")

    await callback.message.edit_text(
        REFERRAL_SETTINGS_MESSAGE.format(
            status="✅ Yoqilgan" if enabled else "🚫 O'chirilgan",
            min_order=format_price(float(min_order)),
            bonus_type_display=BONUS_TYPE_DISPLAY.get(bonus_type, bonus_type),
            bonus_value=bonus_value,
            threshold_count=threshold_count,
            threshold_percent=threshold_percent,
        ),
        reply_markup=referral_settings_keyboard(enabled),
    )


@router.callback_query(F.data == "admin_referral_settings")
async def callback_admin_referral_settings(callback: CallbackQuery) -> None:
    await _render_settings(callback)
    await callback.answer()


@router.callback_query(F.data.startswith("referral_toggle:"))
async def callback_referral_toggle(callback: CallbackQuery) -> None:
    action = callback.data.split(":")[1]
    await db.set_setting("referral_enabled", "1" if action == "on" else "0")
    await db.add_admin_log(callback.from_user.id, "referral_toggle", action)
    await callback.answer(REFERRAL_ENABLED if action == "on" else REFERRAL_DISABLED)
    await _render_settings(callback)


@router.callback_query(F.data == "referral_set_min_order")
async def callback_set_min_order(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(ReferralSettingsStates.waiting_for_min_order)
    await callback.message.edit_text(REFERRAL_SETTINGS_ENTER_MIN_ORDER, reply_markup=cancel_action_keyboard())
    await callback.answer()


@router.message(ReferralSettingsStates.waiting_for_min_order)
async def process_min_order(message: Message, state: FSMContext) -> None:
    value = message.text.strip().replace(" ", "")
    if not is_valid_price(value):
        await message.answer("⚠ Faqat raqam kiriting.", reply_markup=cancel_action_keyboard())
        return
    await db.set_setting("referral_min_order", value)
    await db.add_admin_log(message.from_user.id, "set_referral_min_order", value)
    await state.clear()
    await message.answer(REFERRAL_SETTINGS_UPDATED, reply_markup=referral_settings_keyboard(True))


@router.callback_query(F.data == "referral_set_bonus_type")
async def callback_set_bonus_type(callback: CallbackQuery) -> None:
    await callback.message.edit_text("🎁 Bonus turini tanlang:", reply_markup=referral_bonus_type_keyboard())
    await callback.answer()


@router.callback_query(F.data.startswith("referral_bonus_type:"))
async def callback_bonus_type_chosen(callback: CallbackQuery) -> None:
    bonus_type = callback.data.split(":")[1]
    await db.set_setting("referral_bonus_type", bonus_type)
    await db.add_admin_log(callback.from_user.id, "set_referral_bonus_type", bonus_type)
    await callback.answer(REFERRAL_SETTINGS_UPDATED)
    await _render_settings(callback)


@router.callback_query(F.data == "referral_set_bonus_value")
async def callback_set_bonus_value(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(ReferralSettingsStates.waiting_for_bonus_value)
    await callback.message.edit_text(REFERRAL_SETTINGS_ENTER_BONUS_VALUE, reply_markup=cancel_action_keyboard())
    await callback.answer()


@router.message(ReferralSettingsStates.waiting_for_bonus_value)
async def process_bonus_value(message: Message, state: FSMContext) -> None:
    value = message.text.strip().replace(" ", "")
    if not is_valid_price(value):
        await message.answer("⚠ Faqat raqam kiriting.", reply_markup=cancel_action_keyboard())
        return
    await db.set_setting("referral_bonus_value", value)
    await db.add_admin_log(message.from_user.id, "set_referral_bonus_value", value)
    await state.clear()
    await message.answer(REFERRAL_SETTINGS_UPDATED, reply_markup=referral_settings_keyboard(True))


@router.callback_query(F.data == "referral_set_threshold_count")
async def callback_set_threshold_count(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(ReferralSettingsStates.waiting_for_threshold_count)
    await callback.message.edit_text(REFERRAL_SETTINGS_ENTER_THRESHOLD_COUNT, reply_markup=cancel_action_keyboard())
    await callback.answer()


@router.message(ReferralSettingsStates.waiting_for_threshold_count)
async def process_threshold_count(message: Message, state: FSMContext) -> None:
    value = message.text.strip()
    if not value.isdigit():
        await message.answer("⚠ Faqat raqam kiriting.", reply_markup=cancel_action_keyboard())
        return
    await db.set_setting("referral_threshold_count", value)
    await db.add_admin_log(message.from_user.id, "set_referral_threshold_count", value)
    await state.clear()
    await message.answer(REFERRAL_SETTINGS_UPDATED, reply_markup=referral_settings_keyboard(True))


@router.callback_query(F.data == "referral_set_threshold_percent")
async def callback_set_threshold_percent(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(ReferralSettingsStates.waiting_for_threshold_percent)
    await callback.message.edit_text(REFERRAL_SETTINGS_ENTER_THRESHOLD_PERCENT, reply_markup=cancel_action_keyboard())
    await callback.answer()


@router.message(ReferralSettingsStates.waiting_for_threshold_percent)
async def process_threshold_percent(message: Message, state: FSMContext) -> None:
    value = message.text.strip()
    if not is_valid_number(value):
        await message.answer("⚠ Faqat raqam kiriting.", reply_markup=cancel_action_keyboard())
        return
    await db.set_setting("referral_threshold_percent", value)
    await db.add_admin_log(message.from_user.id, "set_referral_threshold_percent", value)
    await state.clear()
    await message.answer(REFERRAL_SETTINGS_UPDATED, reply_markup=referral_settings_keyboard(True))

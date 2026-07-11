# 📁 JOYLASHUV: aggressor_uc_bot/handlers/admin/promo_management.py
# ⚠ YANGI FAYL
"""
AGGRESSOR UC BOT - Admin Promo kod boshqaruvi handleri.
"""

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database import db
from handlers.admin.panel import IsAdminFilter
from keyboards.admin_kb import (
    admin_panel_keyboard,
    cancel_action_keyboard,
    confirm_delete_promo_keyboard,
    promo_detail_keyboard,
    promo_list_keyboard,
    promo_type_choice_keyboard,
)
from states.new_features_states import PromoCreateStates
from utils.helpers import (
    calculate_expiry_date_from_days,
    format_price,
    is_valid_promo_code_format,
    is_valid_number,
    is_valid_price,
)
from utils.texts_new import (
    PROMO_ADMIN_CHOOSE_TYPE,
    PROMO_ADMIN_CODE_EXISTS,
    PROMO_ADMIN_CREATED_SUCCESS,
    PROMO_ADMIN_ENTER_AMOUNT,
    PROMO_ADMIN_ENTER_CODE,
    PROMO_ADMIN_ENTER_EXPIRY,
    PROMO_ADMIN_ENTER_FREE_UC,
    PROMO_ADMIN_ENTER_MAX_USES,
    PROMO_ADMIN_ENTER_PERCENT,
    PROMO_DELETED_SUCCESS,
    PROMO_DETAIL_ADMIN,
    PROMO_LIST_EMPTY,
    PROMO_LIST_HEADER,
)

router = Router(name="admin_promo_management")
router.message.filter(IsAdminFilter())
router.callback_query.filter(IsAdminFilter())


@router.callback_query(F.data == "admin_promo")
async def callback_admin_promo(callback: CallbackQuery) -> None:
    promos = await db.get_all_promo_codes()
    if not promos:
        await callback.message.edit_text(PROMO_LIST_EMPTY, reply_markup=promo_list_keyboard([]))
        await callback.answer()
        return
    await callback.message.edit_text(PROMO_LIST_HEADER, reply_markup=promo_list_keyboard(promos))
    await callback.answer()


@router.callback_query(F.data == "admin_add_promo")
async def callback_add_promo(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(PromoCreateStates.waiting_for_code)
    await callback.message.edit_text(PROMO_ADMIN_ENTER_CODE, reply_markup=cancel_action_keyboard())
    await callback.answer()


@router.message(PromoCreateStates.waiting_for_code)
async def process_promo_code_input(message: Message, state: FSMContext) -> None:
    code = message.text.strip().upper()
    if not is_valid_promo_code_format(code):
        await message.answer("⚠ Noto'g'ri format. Faqat harf va raqamlar.", reply_markup=cancel_action_keyboard())
        return

    existing = await db.get_promo_code_by_code(code)
    if existing:
        await message.answer(PROMO_ADMIN_CODE_EXISTS, reply_markup=cancel_action_keyboard())
        return

    await state.update_data(promo_code=code)
    await state.set_state(PromoCreateStates.waiting_for_type)
    await message.answer(PROMO_ADMIN_CHOOSE_TYPE, reply_markup=promo_type_choice_keyboard())


@router.callback_query(PromoCreateStates.waiting_for_type, F.data.startswith("promo_type:"))
async def process_promo_type(callback: CallbackQuery, state: FSMContext) -> None:
    promo_type = callback.data.split(":")[1]
    await state.update_data(promo_type=promo_type)

    if promo_type == "percent":
        await state.set_state(PromoCreateStates.waiting_for_percent)
        await callback.message.edit_text(PROMO_ADMIN_ENTER_PERCENT, reply_markup=cancel_action_keyboard())
    elif promo_type == "fixed":
        await state.set_state(PromoCreateStates.waiting_for_amount)
        await callback.message.edit_text(PROMO_ADMIN_ENTER_AMOUNT, reply_markup=cancel_action_keyboard())
    else:
        await state.set_state(PromoCreateStates.waiting_for_free_uc)
        await callback.message.edit_text(PROMO_ADMIN_ENTER_FREE_UC, reply_markup=cancel_action_keyboard())
    await callback.answer()


@router.message(PromoCreateStates.waiting_for_percent)
async def process_promo_percent(message: Message, state: FSMContext) -> None:
    value = message.text.strip()
    if not is_valid_number(value):
        await message.answer("⚠ Faqat raqam kiriting.", reply_markup=cancel_action_keyboard())
        return
    await state.update_data(discount_percent=int(value), discount_amount=0.0, free_uc_amount=0)
    await state.set_state(PromoCreateStates.waiting_for_max_uses)
    await message.answer(PROMO_ADMIN_ENTER_MAX_USES, reply_markup=cancel_action_keyboard())


@router.message(PromoCreateStates.waiting_for_amount)
async def process_promo_amount(message: Message, state: FSMContext) -> None:
    value = message.text.strip().replace(" ", "")
    if not is_valid_price(value):
        await message.answer("⚠ Faqat raqam kiriting.", reply_markup=cancel_action_keyboard())
        return
    await state.update_data(discount_amount=float(value), discount_percent=0, free_uc_amount=0)
    await state.set_state(PromoCreateStates.waiting_for_max_uses)
    await message.answer(PROMO_ADMIN_ENTER_MAX_USES, reply_markup=cancel_action_keyboard())


@router.message(PromoCreateStates.waiting_for_free_uc)
async def process_promo_free_uc(message: Message, state: FSMContext) -> None:
    value = message.text.strip()
    if not is_valid_number(value):
        await message.answer("⚠ Faqat raqam kiriting.", reply_markup=cancel_action_keyboard())
        return
    await state.update_data(free_uc_amount=int(value), discount_percent=0, discount_amount=0.0)
    await state.set_state(PromoCreateStates.waiting_for_max_uses)
    await message.answer(PROMO_ADMIN_ENTER_MAX_USES, reply_markup=cancel_action_keyboard())


@router.message(PromoCreateStates.waiting_for_max_uses)
async def process_promo_max_uses(message: Message, state: FSMContext) -> None:
    value = message.text.strip()
    if not value.isdigit():
        await message.answer("⚠ Faqat raqam kiriting.", reply_markup=cancel_action_keyboard())
        return
    await state.update_data(max_uses=int(value))
    await state.set_state(PromoCreateStates.waiting_for_expiry)
    await message.answer(PROMO_ADMIN_ENTER_EXPIRY, reply_markup=cancel_action_keyboard())


@router.message(PromoCreateStates.waiting_for_expiry)
async def process_promo_expiry(message: Message, state: FSMContext) -> None:
    value = message.text.strip()
    if not value.isdigit():
        await message.answer("⚠ Faqat raqam kiriting.", reply_markup=cancel_action_keyboard())
        return

    data = await state.get_data()
    expires_at = calculate_expiry_date_from_days(int(value))

    promo_id = await db.add_promo_code(
        code=data["promo_code"],
        promo_type=data["promo_type"],
        discount_percent=data.get("discount_percent", 0),
        discount_amount=data.get("discount_amount", 0.0),
        free_uc_amount=data.get("free_uc_amount", 0),
        max_uses=data["max_uses"],
        expires_at=expires_at,
    )
    promo = await db.get_promo_code(promo_id)
    await db.add_admin_log(message.from_user.id, "create_promo", f"code={promo.code}")
    await state.clear()

    await message.answer(
        PROMO_ADMIN_CREATED_SUCCESS.format(
            code=promo.code,
            type_display=promo.type_display(),
            max_uses=promo.max_uses if promo.max_uses > 0 else "cheksiz",
            expiry_display=promo.expires_at or "cheksiz",
        ),
        reply_markup=admin_panel_keyboard(),
    )


@router.callback_query(F.data.startswith("view_promo:"))
async def callback_view_promo(callback: CallbackQuery) -> None:
    promo_id = int(callback.data.split(":")[1])
    promo = await db.get_promo_code(promo_id)
    if not promo:
        await callback.answer("⚠ Topilmadi.", show_alert=True)
        return

    status_display = "✅ Faol" if promo.is_active else "🚫 Nofaol"
    max_uses_display = promo.max_uses if promo.max_uses > 0 else "cheksiz"

    await callback.message.edit_text(
        PROMO_DETAIL_ADMIN.format(
            code=promo.code,
            type_display=promo.type_display(),
            used_count=promo.used_count,
            max_uses_display=max_uses_display,
            status_display=status_display,
            expiry_display=promo.expires_at or "cheksiz",
        ),
        reply_markup=promo_detail_keyboard(promo.id, promo.is_active),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("toggle_promo:"))
async def callback_toggle_promo(callback: CallbackQuery) -> None:
    _, promo_id_str, action = callback.data.split(":")
    promo_id = int(promo_id_str)
    await db.set_promo_code_active(promo_id, action == "on")
    await db.add_admin_log(callback.from_user.id, "toggle_promo", f"id={promo_id}, active={action == 'on'}")
    await callback_view_promo(callback)


@router.callback_query(F.data.startswith("delete_promo:"))
async def callback_delete_promo_confirm(callback: CallbackQuery) -> None:
    promo_id = int(callback.data.split(":")[1])
    promo = await db.get_promo_code(promo_id)
    if not promo:
        await callback.answer("⚠ Topilmadi.", show_alert=True)
        return
    await callback.message.edit_text(
        f"❗ Rostdan ham <b>{promo.code}</b> promo kodni o'chirmoqchimisiz?",
        reply_markup=confirm_delete_promo_keyboard(promo_id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("confirm_delete_promo:"))
async def callback_delete_promo_execute(callback: CallbackQuery) -> None:
    promo_id = int(callback.data.split(":")[1])
    await db.delete_promo_code(promo_id)
    await db.add_admin_log(callback.from_user.id, "delete_promo", f"id={promo_id}")
    await callback.message.edit_text(PROMO_DELETED_SUCCESS, reply_markup=admin_panel_keyboard())
    await callback.answer()

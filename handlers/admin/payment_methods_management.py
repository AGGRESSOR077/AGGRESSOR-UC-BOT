# 📁 JOYLASHUV: aggressor_uc_bot/handlers/admin/payment_methods_management.py
# ⚠ YANGI FAYL
"""
AGGRESSOR UC BOT - Admin To'lov usullari boshqaruvi handleri.
"""

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database import db
from handlers.admin.panel import IsAdminFilter
from keyboards.admin_kb import (
    admin_panel_keyboard,
    cancel_action_keyboard,
    payment_method_detail_keyboard,
    payment_methods_list_keyboard,
)
from states.new_features_states import PaymentMethodCreateStates
from utils.helpers import mask_card_number
from utils.texts_new import (
    PAYMENT_METHOD_ADD_ENTER_CARD_NUMBER,
    PAYMENT_METHOD_ADD_ENTER_CARD_OWNER,
    PAYMENT_METHOD_ADD_ENTER_NAME,
    PAYMENT_METHOD_ADD_SUCCESS,
    PAYMENT_METHOD_DELETE_SUCCESS,
    PAYMENT_METHOD_LIST_EMPTY,
    PAYMENT_METHOD_LIST_HEADER,
)

router = Router(name="admin_payment_methods_management")
router.message.filter(IsAdminFilter())
router.callback_query.filter(IsAdminFilter())


@router.callback_query(F.data == "admin_payment_methods")
async def callback_admin_payment_methods(callback: CallbackQuery) -> None:
    methods = await db.get_all_payment_methods()
    if not methods:
        await callback.message.edit_text(PAYMENT_METHOD_LIST_EMPTY, reply_markup=payment_methods_list_keyboard([]))
        await callback.answer()
        return
    await callback.message.edit_text(PAYMENT_METHOD_LIST_HEADER, reply_markup=payment_methods_list_keyboard(methods))
    await callback.answer()


@router.callback_query(F.data == "admin_add_payment_method")
async def callback_add_payment_method(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(PaymentMethodCreateStates.waiting_for_name)
    await callback.message.edit_text(PAYMENT_METHOD_ADD_ENTER_NAME, reply_markup=cancel_action_keyboard())
    await callback.answer()


@router.message(PaymentMethodCreateStates.waiting_for_name)
async def process_payment_method_name(message: Message, state: FSMContext) -> None:
    await state.update_data(pm_name=message.text.strip())
    await state.set_state(PaymentMethodCreateStates.waiting_for_card_number)
    await message.answer(PAYMENT_METHOD_ADD_ENTER_CARD_NUMBER, reply_markup=cancel_action_keyboard())


@router.message(PaymentMethodCreateStates.waiting_for_card_number)
async def process_payment_method_card_number(message: Message, state: FSMContext) -> None:
    await state.update_data(pm_card_number=message.text.strip())
    await state.set_state(PaymentMethodCreateStates.waiting_for_card_owner)
    await message.answer(PAYMENT_METHOD_ADD_ENTER_CARD_OWNER, reply_markup=cancel_action_keyboard())


@router.message(PaymentMethodCreateStates.waiting_for_card_owner)
async def process_payment_method_card_owner(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    card_owner = message.text.strip()

    await db.add_payment_method(
        name=data["pm_name"],
        card_number=data["pm_card_number"],
        card_owner=card_owner,
    )
    await db.add_admin_log(message.from_user.id, "add_payment_method", data["pm_name"])
    await state.clear()

    await message.answer(PAYMENT_METHOD_ADD_SUCCESS, reply_markup=admin_panel_keyboard())


@router.callback_query(F.data.startswith("view_payment_method:"))
async def callback_view_payment_method(callback: CallbackQuery) -> None:
    method_id = int(callback.data.split(":")[1])
    method = await db.get_payment_method(method_id)
    if not method:
        await callback.answer("⚠ Topilmadi.", show_alert=True)
        return

    status = "✅ Faol" if method.is_active else "🚫 Nofaol"
    text = (
        f"💳 <b>{method.name}</b>\n\n"
        f"Karta: <code>{mask_card_number(method.card_number)}</code>\n"
        f"Egasi: {method.card_owner}\n"
        f"Holati: {status}"
    )
    await callback.message.edit_text(text, reply_markup=payment_method_detail_keyboard(method.id, method.is_active))
    await callback.answer()


@router.callback_query(F.data.startswith("toggle_payment_method:"))
async def callback_toggle_payment_method(callback: CallbackQuery) -> None:
    _, method_id_str, action = callback.data.split(":")
    method_id = int(method_id_str)
    await db.set_payment_method_active(method_id, action == "on")
    await db.add_admin_log(callback.from_user.id, "toggle_payment_method", f"id={method_id}, active={action == 'on'}")
    await callback_view_payment_method(callback)


@router.callback_query(F.data.startswith("delete_payment_method:"))
async def callback_delete_payment_method(callback: CallbackQuery) -> None:
    method_id = int(callback.data.split(":")[1])
    await db.delete_payment_method(method_id)
    await db.add_admin_log(callback.from_user.id, "delete_payment_method", f"id={method_id}")
    await callback.message.edit_text(PAYMENT_METHOD_DELETE_SUCCESS, reply_markup=admin_panel_keyboard())
    await callback.answer()

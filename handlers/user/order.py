# 📁 JOYLASHUV: aggressor_uc_bot/handlers/user/order.py
# ⚠ MAVJUD FAYL — to'liq almashtiring
"""
AGGRESSOR UC BOT - Buyurtma yaratish handleri.

Bu modul mijozning to'liq buyurtma jarayonini boshqaradi:
1. Paket tanlash
2. PUBG UID kiritish
3. (YANGI) Promo kod kiritish/o'tkazib yuborish
4. Karta raqamini ko'rsatish
5. Chek qabul qilish
6. Buyurtmani database'ga yozish, referral bonus va adminga xabar yuborish
"""

import asyncio
import time

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from config import config
from database import db
from database.models import Order
from keyboards.admin_kb import order_action_keyboard
from keyboards.user_kb import (
    back_to_menu_keyboard,
    cancel_order_keyboard,
    main_menu_keyboard,
    promo_entry_keyboard,
)
from states.new_features_states import PromoApplyStates
from states.order_states import OrderStates
from utils.helpers import escape_html, format_price, get_username_display, is_valid_pubg_uid
from utils.texts import (
    NEW_ORDER_ADMIN_MESSAGE,
    ORDER_CREATED_SUCCESS,
    ORDER_ENTER_UID,
    ORDER_RECEIPT_INVALID,
    ORDER_UID_INVALID,
    CANCEL_ACTION,
    WELCOME_MESSAGE,
)
from utils.texts_new import PROMO_ENTER_CODE_PROMPT

router = Router(name="user_order")

# ---- YANGI: Auto Cancel sozlamalari ----
AUTO_CANCEL_MINUTES = 15
AUTO_CANCEL_MESSAGE = (
    "⏰ Vaqt tugagani sababli buyurtma jarayoni bekor qilindi.\n"
    "Agar hali ham xarid qilishni istasangiz, qaytadan buyurtma bering."
)


async def _schedule_auto_cancel(bot, state: FSMContext, telegram_id: int, token: str) -> None:
    """
    YANGI: Auto Cancel — belgilangan vaqt o'tgach, agar foydalanuvchi
    hali ham chek yubormagan bo'lsa, jarayonni avtomatik bekor qiladi.
    """
    await asyncio.sleep(AUTO_CANCEL_MINUTES * 60)

    data = await state.get_data()
    if data.get("session_token") != token:
        return

    current_state = await state.get_state()
    active_states = (PromoApplyStates.waiting_for_code.state, OrderStates.waiting_for_receipt.state)
    if current_state in active_states:
        await state.clear()
        try:
            await bot.send_message(chat_id=telegram_id, text=AUTO_CANCEL_MESSAGE)
        except Exception:
            pass


@router.callback_query(F.data.startswith("select_package:"))
async def callback_select_package(callback: CallbackQuery, state: FSMContext) -> None:
    """Mijoz paketni tanlaganda ishga tushadi va UID so'raydi."""
    package_id = int(callback.data.split(":")[1])
    package = await db.get_package(package_id)

    if not package or not package.is_active:
        await callback.answer("⚠ Bu paket endi mavjud emas.", show_alert=True)
        return

    await state.update_data(
        package_id=package.id,
        package_name=package.display_name(),
        uc_amount=package.uc_amount,
        price=package.price,
    )
    await state.set_state(OrderStates.waiting_for_uid)

    await callback.message.edit_text(
        ORDER_ENTER_UID.format(
            package_name=package.display_name(),
            price=package.display_price(),
        ),
        reply_markup=cancel_order_keyboard(),
    )
    await callback.answer()


@router.message(OrderStates.waiting_for_uid)
async def process_uid(message: Message, state: FSMContext) -> None:
    """
    Mijoz PUBG UID kiritganda ishga tushadi va to'g'riligini tekshiradi.

    YANGI: UID qabul qilingach endi Promo kod kiritish bosqichi
    ko'rsatiladi va Auto Cancel fon taymeri ishga tushadi.
    """
    uid = (message.text or "").strip()

    if not is_valid_pubg_uid(uid):
        await message.answer(
            ORDER_UID_INVALID,
            reply_markup=cancel_order_keyboard(),
        )
        return

    session_token = str(time.monotonic())
    await state.update_data(pubg_uid=uid, session_token=session_token)
    await state.set_state(PromoApplyStates.waiting_for_code)

    await message.answer(PROMO_ENTER_CODE_PROMPT, reply_markup=promo_entry_keyboard())

    asyncio.create_task(
        _schedule_auto_cancel(message.bot, state, message.from_user.id, session_token)
    )


@router.message(OrderStates.waiting_for_receipt, F.photo)
async def process_receipt(message: Message, state: FSMContext) -> None:
    """
    Mijoz chek rasmini yuborganda ishga tushadi.

    Buyurtmani database'ga yozadi, promo kod ishlatilgan bo'lsa qayd
    etadi, referral bonusini beradi va adminga xabar yuboradi.
    """
    data = await state.get_data()

    user = await db.get_user_by_telegram_id(message.from_user.id)
    if user is None:
        await db.add_user(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            full_name=message.from_user.full_name,
        )
        user = await db.get_user_by_telegram_id(message.from_user.id)

    receipt_photo_id = message.photo[-1].file_id

    order_id = await db.create_order(
        user_id=user.id,
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        pubg_uid=data["pubg_uid"],
        package_id=data["package_id"],
        package_name=data["package_name"],
        uc_amount=data["uc_amount"],
        price=data["price"],
        receipt_photo_id=receipt_photo_id,
    )
    order_number = Order.ORDER_NUMBER_OFFSET + order_id

    # ---- YANGI: Promo kod ishlatilgan bo'lsa qayd etamiz ----
    applied_promo_id = data.get("applied_promo_id")
    free_uc_note = ""
    if applied_promo_id:
        await db.record_promo_usage(applied_promo_id, message.from_user.id, order_id)
        promo = await db.get_promo_code(applied_promo_id)
        if promo and promo.promo_type == "free_uc" and promo.free_uc_amount:
            free_uc_note = f"\n🎁 Promo orqali qo'shimcha {promo.free_uc_amount} UC beriladi!"

    await message.answer(
        ORDER_CREATED_SUCCESS.format(
            order_id=order_number,
            package_name=data["package_name"],
            price=format_price(data["price"]),
        )
        + free_uc_note,
        reply_markup=main_menu_keyboard(),
    )
    await state.clear()

    # ---- YANGI: Referral bonusi ----
    if user.referred_by:
        existing_referral = await db.get_referral_by_referred(message.from_user.id)
        min_order_raw = await db.get_setting("referral_min_order", "0")
        min_order = float(min_order_raw) if min_order_raw else 0.0
        if not existing_referral and data["price"] >= min_order:
            bonus_value_raw = await db.get_setting("referral_bonus_value", "0")
            bonus_value = float(bonus_value_raw) if bonus_value_raw else 0.0
            await db.add_referral(user.referred_by, message.from_user.id, bonus_amount=bonus_value)
            await db.increase_bonus_balance(user.referred_by, bonus_value)
            try:
                await message.bot.send_message(
                    chat_id=user.referred_by,
                    text=(
                        "🎉 Sizning havolangiz orqali yangi xarid amalga oshirildi!\n"
                        f"💰 Bonusingiz: {format_price(bonus_value)}"
                    ),
                )
            except Exception:
                pass

    username_display = get_username_display(message.from_user.username, message.from_user.id)
    admin_caption = (
        NEW_ORDER_ADMIN_MESSAGE.format(
            order_id=order_number,
            username=username_display,
            telegram_id=message.from_user.id,
            pubg_uid=data["pubg_uid"],
            package_name=data["package_name"],
            price=format_price(data["price"]),
        )
        + free_uc_note
    )

    for admin_id in config.ADMIN_IDS:
        try:
            await message.bot.send_photo(
                chat_id=admin_id,
                photo=receipt_photo_id,
                caption=admin_caption,
                reply_markup=order_action_keyboard(order_id, message.from_user.id),
            )
        except Exception:
            continue


@router.message(OrderStates.waiting_for_receipt)
async def process_receipt_invalid(message: Message) -> None:
    """Agar mijoz chek o'rniga rasm bo'lmagan narsa yuborsa ishga tushadi."""
    await message.answer(
        ORDER_RECEIPT_INVALID,
        reply_markup=cancel_order_keyboard(),
    )


@router.callback_query(F.data == "cancel_order")
async def callback_cancel_order(callback: CallbackQuery, state: FSMContext) -> None:
    """Mijoz buyurtma jarayonini bekor qilganda ishga tushadi."""
    await state.clear()

    full_name_safe = escape_html(callback.from_user.full_name or "do'stim")

    await callback.message.edit_text(
        WELCOME_MESSAGE.format(full_name=full_name_safe),
        reply_markup=main_menu_keyboard(),
    )
    await callback.answer(CANCEL_ACTION)

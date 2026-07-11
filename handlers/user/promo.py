# 📁 JOYLASHUV: aggressor_uc_bot/handlers/user/promo.py
# ⚠ YANGI FAYL — ushbu nom bilan saqlang
# ℹ️ ESLATMA: Bu fayl to'liq ishlashi uchun `handlers/user/order.py` faylida
# UID qabul qilingandan so'ng holat OrderStates.waiting_for_receipt ga emas,
# balki PromoApplyStates.waiting_for_code ga o'tkazilishi kerak (bu o'zgarish
# navbatdagi "handlers/user/order.py (kichik modifikatsiya)" faylida amalga oshiriladi).
"""
AGGRESSOR UC BOT - Promo kod handleri.

Bu modul mijoz buyurtma jarayonida promo kod kiritishi yoki
o'tkazib yuborishi imkoniyatini boshqaradi.
"""

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from config import config
from database import db
from keyboards.user_kb import cancel_order_keyboard, promo_entry_keyboard
from states.new_features_states import PromoApplyStates
from states.order_states import OrderStates
from utils.helpers import apply_fixed_discount, apply_percent_discount, format_price
from utils.texts import ORDER_PAYMENT_INFO
from utils.texts_new import (
    PROMO_CODE_ALREADY_USED,
    PROMO_CODE_APPLIED,
    PROMO_CODE_INVALID,
    PROMO_CODE_SKIPPED,
)

router = Router(name="user_promo")


async def _show_payment_info(message, state: FSMContext) -> None:
    """
    Promo bosqichi tugagandan so'ng to'lov ma'lumotlarini ko'rsatadi
    va holatni OrderStates.waiting_for_receipt ga o'tkazadi.

    Bu funksiya `handlers/user/order.py` dagi to'lov ko'rsatish
    logikasi bilan bir xil ishlaydi — promo qo'llanilgandan keyin
    davom etish uchun ishlatiladi.
    """
    data = await state.get_data()
    price = data["price"]

    card_number = await db.get_setting("card_number", config.CARD_NUMBER)
    card_owner = await db.get_setting("card_owner", config.CARD_OWNER)

    await state.set_state(OrderStates.waiting_for_receipt)

    await message.answer(
        ORDER_PAYMENT_INFO.format(
            pubg_uid=data["pubg_uid"],
            card_number=card_number,
            card_owner=card_owner,
            price=format_price(price),
        ),
        reply_markup=cancel_order_keyboard(),
    )


@router.callback_query(PromoApplyStates.waiting_for_code, F.data == "skip_promo")
async def callback_skip_promo(callback: CallbackQuery, state: FSMContext) -> None:
    """Foydalanuvchi promo kodni kiritmasdan o'tkazib yuborganda ishga tushadi."""
    await callback.answer(PROMO_CODE_SKIPPED)
    await _show_payment_info(callback.message, state)


@router.message(PromoApplyStates.waiting_for_code)
async def process_promo_code(message: Message, state: FSMContext) -> None:
    """
    Foydalanuvchi promo kod matnini kiritganda uni tekshiradi.

    Agar kod to'g'ri va hali ishlatilmagan bo'lsa, narxga chegirma
    qo'llanadi (yoki bepul UC belgisi FSM ma'lumotiga yoziladi) va
    natija `applied_promo_id` sifatida keyingi bosqichga (buyurtma
    yaratilganda promo ishlatilganini belgilash uchun) saqlanadi.
    """
    code = message.text.strip().upper()
    promo = await db.get_promo_code_by_code(code)

    if not promo or not promo.is_usable():
        await message.answer(PROMO_CODE_INVALID, reply_markup=promo_entry_keyboard())
        return

    already_used = await db.has_user_used_promo(promo.id, message.from_user.id)
    if already_used:
        await message.answer(PROMO_CODE_ALREADY_USED, reply_markup=promo_entry_keyboard())
        return

    data = await state.get_data()
    original_price = data["price"]

    if promo.promo_type == "percent":
        new_price = apply_percent_discount(original_price, promo.discount_percent)
        description = f"{promo.discount_percent}% chegirma qo'llanildi"
    elif promo.promo_type == "fixed":
        new_price = apply_fixed_discount(original_price, promo.discount_amount)
        description = f"{format_price(promo.discount_amount)} chegirma qo'llanildi"
    else:  # "free_uc"
        new_price = original_price
        description = f"Buyurtmangizga qo'shimcha {promo.free_uc_amount} UC bepul qo'shiladi"

    await state.update_data(price=new_price, applied_promo_id=promo.id)

    await message.answer(
        PROMO_CODE_APPLIED.format(
            promo_description=description,
            new_price=format_price(new_price),
        )
    )

    await _show_payment_info(message, state)

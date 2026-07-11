# 📁 JOYLASHUV: aggressor_uc_bot/handlers/user/uc_calculator.py
# ⚠ YANGI FAYL — ushbu nom bilan saqlang
"""
AGGRESSOR UC BOT - UC Calculator handleri.

Bu modul "🧮 UC Calculator" bo'limini boshqaradi: foydalanuvchi
UC miqdori yoki narx kiritsa, bot mavjud paketlar asosida
o'rtacha kursni hisoblab, taxminiy natijani ko'rsatadi.
"""

import re

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database import db
from keyboards.user_kb import uc_calculator_keyboard
from states.new_features_states import UCCalculatorStates
from utils.helpers import (
    calculate_average_rate_per_uc,
    calculate_price_by_uc,
    calculate_uc_by_price,
    format_price,
)
from utils.texts_new import (
    UC_CALCULATOR_INVALID_INPUT,
    UC_CALCULATOR_NO_RATE,
    UC_CALCULATOR_PROMPT,
    UC_CALCULATOR_RESULT_BY_PRICE,
    UC_CALCULATOR_RESULT_BY_UC,
)

router = Router(name="user_uc_calculator")


@router.callback_query(F.data == "uc_calculator")
async def callback_uc_calculator(callback: CallbackQuery, state: FSMContext) -> None:
    """"🧮 UC Calculator" tugmasi bosilganda kiritish so'raladi."""
    await state.set_state(UCCalculatorStates.waiting_for_input)
    await callback.message.edit_text(
        UC_CALCULATOR_PROMPT,
        reply_markup=uc_calculator_keyboard(),
    )
    await callback.answer()


@router.message(UCCalculatorStates.waiting_for_input)
async def process_uc_calculator_input(message: Message, state: FSMContext) -> None:
    """
    Foydalanuvchi UC miqdori yoki narx kiritganda avtomatik hisoblaydi.

    Agar matn "so'm" yoki "som" so'zini o'z ichiga olsa — bu narx
    sifatida, aks holda UC miqdori sifatida qabul qilinadi.
    """
    raw_text = message.text.strip().lower()
    digits_only = re.sub(r"[^\d]", "", raw_text)

    if not digits_only:
        await message.answer(
            UC_CALCULATOR_INVALID_INPUT,
            reply_markup=uc_calculator_keyboard(),
        )
        return

    value = int(digits_only)

    packages = await db.get_all_packages(only_active=True)
    rate_per_uc = calculate_average_rate_per_uc(packages)

    if rate_per_uc <= 0:
        await message.answer(
            UC_CALCULATOR_NO_RATE,
            reply_markup=uc_calculator_keyboard(),
        )
        return

    is_price_input = "so'm" in raw_text or "som" in raw_text or "sum" in raw_text

    if is_price_input:
        uc_amount = calculate_uc_by_price(value, rate_per_uc)
        await message.answer(
            UC_CALCULATOR_RESULT_BY_PRICE.format(
                price=format_price(value),
                uc_amount=uc_amount,
                rate_per_uc=format_price(rate_per_uc),
            ),
            reply_markup=uc_calculator_keyboard(),
        )
    else:
        price = calculate_price_by_uc(value, rate_per_uc)
        await message.answer(
            UC_CALCULATOR_RESULT_BY_UC.format(
                uc_amount=value,
                price=format_price(price),
                rate_per_uc=format_price(rate_per_uc),
            ),
            reply_markup=uc_calculator_keyboard(),
        )

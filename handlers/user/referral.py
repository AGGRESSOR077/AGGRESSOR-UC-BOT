# 📁 JOYLASHUV: aggressor_uc_bot/handlers/user/referral.py
# ⚠ YANGI FAYL — ushbu nom bilan saqlang
"""
AGGRESSOR UC BOT - Referral tizimi handleri.

Bu modul "🤝 Referral" bo'limini boshqaradi: foydalanuvchiga
referral havola beradi, taklif qilinganlar sonini va bonus
balansini ko'rsatadi.
"""

from aiogram import F, Router
from aiogram.types import CallbackQuery

from config import config
from database import db
from keyboards.user_kb import referral_menu_keyboard
from utils.helpers import format_price, generate_referral_code
from utils.texts_new import (
    REFERRAL_DISABLED_MESSAGE,
    REFERRAL_MENU_MESSAGE,
    REFERRAL_THRESHOLD_INFO,
    REFERRAL_THRESHOLD_REACHED,
)

router = Router(name="user_referral")


@router.callback_query(F.data == "referral_menu")
async def callback_referral_menu(callback: CallbackQuery) -> None:
    """"🤝 Referral" tugmasi bosilganda referral havola va statistikani ko'rsatadi."""
    referral_enabled = await db.get_setting("referral_enabled", "1")

    if referral_enabled != "1":
        await callback.message.edit_text(
            REFERRAL_DISABLED_MESSAGE,
            reply_markup=referral_menu_keyboard(),
        )
        await callback.answer()
        return

    telegram_id = callback.from_user.id
    user = await db.get_user_by_telegram_id(telegram_id)

    # Agar foydalanuvchida hali referral kod bo'lmasa, yaratamiz
    if not user.referral_code:
        new_code = generate_referral_code(telegram_id)
        await db.set_user_referral_code(telegram_id, new_code)
        referral_code = new_code
    else:
        referral_code = user.referral_code

    referral_link = f"https://t.me/{config.BOT_USERNAME}?start={referral_code}"
    referrals_count = await db.count_referrals_by_user(telegram_id)

    threshold_count_raw = await db.get_setting("referral_threshold_count", "0")
    threshold_percent_raw = await db.get_setting("referral_threshold_percent", "0")
    threshold_count = int(threshold_count_raw) if threshold_count_raw.isdigit() else 0
    threshold_percent = int(threshold_percent_raw) if threshold_percent_raw.isdigit() else 0

    if threshold_count > 0:
        if referrals_count >= threshold_count:
            threshold_info = REFERRAL_THRESHOLD_REACHED.format(
                threshold_count=threshold_count,
                threshold_percent=threshold_percent,
            )
        else:
            threshold_info = REFERRAL_THRESHOLD_INFO.format(
                threshold_count=threshold_count,
                threshold_percent=threshold_percent,
            )
    else:
        threshold_info = ""

    await callback.message.edit_text(
        REFERRAL_MENU_MESSAGE.format(
            referral_link=referral_link,
            referrals_count=referrals_count,
            bonus_balance=format_price(user.bonus_balance),
            threshold_info=threshold_info,
        ),
        reply_markup=referral_menu_keyboard(),
    )
    await callback.answer()

# 📁 JOYLASHUV: aggressor_uc_bot/handlers/user/rating.py
# ⚠ YANGI FAYL — ushbu nom bilan saqlang
"""
AGGRESSOR UC BOT - Reyting handleri.

Bu modul buyurtma tugagach foydalanuvchi 1-5 ⭐ baho berish
jarayonini boshqaradi.
"""

from aiogram import F, Router
from aiogram.types import CallbackQuery

from database import db
from keyboards.user_kb import order_detail_user_keyboard, rating_keyboard
from utils.texts_new import RATING_ALREADY_RATED, RATING_THANKS_MESSAGE

router = Router(name="user_rating")


@router.callback_query(F.data.startswith("rate_prompt:"))
async def callback_rate_prompt(callback: CallbackQuery) -> None:
    """Foydalanuvchi "⭐ Baho berish" tugmasini bosganda yulduzcha tanlovini chiqaradi."""
    order_id = int(callback.data.split(":")[1])
    order = await db.get_order(order_id)

    if not order or order.telegram_id != callback.from_user.id:
        await callback.answer("⚠ Buyurtma topilmadi.", show_alert=True)
        return

    if order.status != "completed":
        await callback.answer("⚠ Faqat bajarilgan buyurtmalarga baho berish mumkin.", show_alert=True)
        return

    if order.rating is not None:
        await callback.answer(RATING_ALREADY_RATED, show_alert=True)
        return

    await callback.message.edit_text(
        "⭐ Xizmatimizni qanday baholaysiz?",
        reply_markup=rating_keyboard(order.id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("rate_order:"))
async def callback_rate_order(callback: CallbackQuery) -> None:
    """Foydalanuvchi yulduzcha sonini tanlaganda reytingni saqlaydi."""
    _, order_id_str, stars_str = callback.data.split(":")
    order_id = int(order_id_str)
    stars = int(stars_str)

    order = await db.get_order(order_id)

    if not order or order.telegram_id != callback.from_user.id:
        await callback.answer("⚠ Buyurtma topilmadi.", show_alert=True)
        return

    if order.rating is not None:
        await callback.answer(RATING_ALREADY_RATED, show_alert=True)
        return

    await db.set_order_rating(order_id, stars)

    await callback.message.edit_text(
        RATING_THANKS_MESSAGE.format(rating=stars),
        reply_markup=order_detail_user_keyboard(order.id, show_rating=False),
    )
    await callback.answer()

# 📁 JOYLASHUV: aggressor_uc_bot/services/auto_cancel.py
# ⚠ YANGI FAYL
"""
AGGRESSOR UC BOT - Auto Cancel fon jarayoni.

Vaqtida chek yuborilmagan (muddati o'tgan) "pending" buyurtmalarni
avtomatik ravishda "cancelled" holatiga o'tkazadi va foydalanuvchiga
xabar beradi.
"""

import asyncio
import logging

from aiogram import Bot

from database import db
from utils.texts_new import ORDER_AUTO_CANCELLED_ADMIN_LOG, ORDER_AUTO_CANCELLED_USER

logger = logging.getLogger(__name__)

AUTO_CANCEL_CHECK_INTERVAL_SECONDS = 60
SYSTEM_LOG_ADMIN_ID = 0


async def check_and_cancel_expired_orders(bot: Bot) -> None:
    """Muddati o'tgan barcha "pending" buyurtmalarni bir marta tekshiradi va bekor qiladi."""
    expired_orders = await db.get_expired_pending_orders()

    for order in expired_orders:
        await db.update_order_status(order.id, "cancelled")
        await db.add_admin_log(
            SYSTEM_LOG_ADMIN_ID,
            "auto_cancel",
            ORDER_AUTO_CANCELLED_ADMIN_LOG.format(order_number=order.order_number),
        )

        try:
            await bot.send_message(
                chat_id=order.telegram_id,
                text=ORDER_AUTO_CANCELLED_USER.format(order_number=order.order_number),
            )
        except Exception:
            logger.warning("Auto-cancel xabarini yuborib bo'lmadi: telegram_id=%s", order.telegram_id)


async def start_auto_cancel_scheduler(bot: Bot) -> None:
    """
    Auto Cancel jarayonini fon rejimida doimiy ishga tushiradi.

    Bu funksiya `bot.py` ichida `asyncio.create_task(...)` orqali
    polling bilan bir vaqtda ishga tushiriladi.
    """
    while True:
        try:
            await check_and_cancel_expired_orders(bot)
        except Exception:
            logger.exception("Auto-cancel jarayonida kutilmagan xatolik yuz berdi.")
        await asyncio.sleep(AUTO_CANCEL_CHECK_INTERVAL_SECONDS)

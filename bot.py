# 📁 JOYLASHUV: aggressor_uc_bot/bot.py
# ⚠ MAVJUD FAYL — to'liq almashtiring
"""
AGGRESSOR UC BOT - Asosiy kirish nuqtasi.

Bu fayl botni ishga tushirish uchun barcha komponentlarni
(Bot, Dispatcher, Router'lar, Middleware'lar, Database) bir joyga
yig'adi va polling rejimida botni ishga tushiradi.
"""

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import config
from database import db
from handlers.admin import banner_management as admin_banner_management
from handlers.admin import broadcast as admin_broadcast
from handlers.admin import news_management as admin_news_management
from handlers.admin import orders as admin_orders
from handlers.admin import packages_manage as admin_packages_manage
from handlers.admin import panel as admin_panel
from handlers.admin import payment_methods_management as admin_payment_methods_management
from handlers.admin import promo_management as admin_promo_management
from handlers.admin import referral_settings as admin_referral_settings
from handlers.admin import settings as admin_settings
from handlers.admin import statistics as admin_statistics
from handlers.admin import users_management as admin_users_management
from handlers.user import contact as user_contact
from handlers.user import my_orders as user_my_orders
from handlers.user import order as user_order
from handlers.user import packages as user_packages
from handlers.user import promo as user_promo
from handlers.user import rating as user_rating
from handlers.user import referral as user_referral
from handlers.user import start as user_start
from handlers.user import uc_calculator as user_uc_calculator
from middlewares.antispam import AntiSpamMiddleware
from middlewares.ban_check import BanCheckMiddleware
from middlewares.throttling import ThrottlingMiddleware
from services.auto_cancel import start_auto_cancel_scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


async def on_startup(bot: Bot) -> None:
    """Bot ishga tushganda bajariladigan tayyorgarlik ishlari."""
    await db.create_tables()
    logger.info("Database jadvallari tayyorlandi.")

    for admin_id in config.ADMIN_IDS:
        await db.add_admin(telegram_id=admin_id)
    logger.info("Adminlar (%s ta) database'ga qo'shildi.", len(config.ADMIN_IDS))

    # ---- YANGI: Auto Cancel fon jarayonini ishga tushirish ----
    asyncio.create_task(start_auto_cancel_scheduler(bot))
    logger.info("Auto Cancel fon jarayoni ishga tushirildi.")

    bot_info = await bot.get_me()
    logger.info("Bot ishga tushdi: @%s (ID: %s)", bot_info.username, bot_info.id)


async def on_shutdown(bot: Bot) -> None:
    """Bot to'xtaganda bajariladigan yakuniy ishlar."""
    logger.info("Bot to'xtatilmoqda...")
    await bot.session.close()


def register_routers(dp: Dispatcher) -> None:
    """Barcha handler routerlarini Dispatcher'ga ro'yxatdan o'tkazadi."""
    # Admin routerlar (aniqroq bo'lgani uchun oldinroq ro'yxatdan o'tadi)
    dp.include_router(admin_panel.router)
    dp.include_router(admin_orders.router)
    dp.include_router(admin_packages_manage.router)
    dp.include_router(admin_broadcast.router)
    dp.include_router(admin_statistics.router)
    dp.include_router(admin_settings.router)
    # ---- YANGI: Admin routerlar ----
    dp.include_router(admin_users_management.router)
    dp.include_router(admin_promo_management.router)
    dp.include_router(admin_banner_management.router)
    dp.include_router(admin_news_management.router)
    dp.include_router(admin_payment_methods_management.router)
    dp.include_router(admin_referral_settings.router)

    # Mijoz routerlar
    dp.include_router(user_start.router)
    dp.include_router(user_packages.router)
    dp.include_router(user_promo.router)
    dp.include_router(user_order.router)
    dp.include_router(user_contact.router)
    # ---- YANGI: Mijoz routerlar ----
    dp.include_router(user_my_orders.router)
    dp.include_router(user_rating.router)
    dp.include_router(user_referral.router)
    dp.include_router(user_uc_calculator.router)


def register_middlewares(dp: Dispatcher) -> None:
    """Barcha middleware'larni Dispatcher'ga ro'yxatdan o'tkazadi."""
    ban_check_middleware = BanCheckMiddleware()
    antispam_middleware = AntiSpamMiddleware(window_seconds=3.0, max_requests=6, restrict_seconds=30)
    throttling_middleware = ThrottlingMiddleware(rate_limit=0.7)

    # ---- YANGI: Ban tekshiruvi va Anti Spam eng birinchi ishlaydi ----
    dp.message.middleware(ban_check_middleware)
    dp.callback_query.middleware(ban_check_middleware)
    dp.message.middleware(antispam_middleware)
    dp.callback_query.middleware(antispam_middleware)

    dp.message.middleware(throttling_middleware)
    dp.callback_query.middleware(throttling_middleware)


async def main() -> None:
    """Botni ishga tushiruvchi asosiy asinxron funksiya."""
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    register_middlewares(dp)
    register_routers(dp)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Polling rejimida bot ishga tushirilmoqda...")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot foydalanuvchi tomonidan to'xtatildi.")

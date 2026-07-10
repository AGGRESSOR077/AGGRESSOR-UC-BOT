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
from handlers.admin import broadcast as admin_broadcast
from handlers.admin import orders as admin_orders
from handlers.admin import packages_manage as admin_packages_manage
from handlers.admin import panel as admin_panel
from handlers.admin import settings as admin_settings
from handlers.admin import statistics as admin_statistics
from handlers.user import contact as user_contact
from handlers.user import order as user_order
from handlers.user import packages as user_packages
from handlers.user import start as user_start
from middlewares.throttling import ThrottlingMiddleware

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

    # Mijoz routerlar
    dp.include_router(user_start.router)
    dp.include_router(user_packages.router)
    dp.include_router(user_order.router)
    dp.include_router(user_contact.router)


def register_middlewares(dp: Dispatcher) -> None:
    """Barcha middleware'larni Dispatcher'ga ro'yxatdan o'tkazadi."""
    throttling_middleware = ThrottlingMiddleware(rate_limit=0.7)
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

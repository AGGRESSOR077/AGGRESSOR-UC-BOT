# 📁 JOYLASHUV: aggressor_uc_bot/middlewares/ban_check.py
# ⚠ YANGI FAYL
"""
AGGRESSOR UC BOT - Ban tekshiruvi middleware.

Ban qilingan foydalanuvchilar botdagi hech qanday funksiyadan
(adminlar bundan mustasno) foydalana olmasligini ta'minlaydi.
"""

from typing import Any, Awaitable, Callable, Dict, Optional

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from config import config
from database import db
from utils.texts_new import USER_IS_BANNED_MESSAGE


class BanCheckMiddleware(BaseMiddleware):
    """Ban qilingan foydalanuvchilarni har qanday handlerdan to'sadi."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user_id = self._extract_user_id(event)
        if user_id is None:
            return await handler(event, data)

        # Adminlar ban tekshiruvidan mustasno
        if config.is_admin(user_id):
            return await handler(event, data)

        user = await db.get_user_by_telegram_id(user_id)
        if user and user.is_banned:
            text = USER_IS_BANNED_MESSAGE.format(reason=user.ban_reason or "Sabab ko'rsatilmagan")
            if isinstance(event, CallbackQuery):
                await event.answer(text, show_alert=True)
            elif isinstance(event, Message):
                await event.answer(text)
            return None

        return await handler(event, data)

    @staticmethod
    def _extract_user_id(event: TelegramObject) -> Optional[int]:
        """Message yoki CallbackQuery obyektidan foydalanuvchi ID sini oladi."""
        if isinstance(event, Message) and event.from_user:
            return event.from_user.id
        if isinstance(event, CallbackQuery) and event.from_user:
            return event.from_user.id
        return None

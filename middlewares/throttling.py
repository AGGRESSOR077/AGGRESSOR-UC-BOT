"""
AGGRESSOR UC BOT - Throttling (flood control) middleware.

Bu modul foydalanuvchilarning botga juda tez-tez so'rov yuborishini
(spam/flood) cheklash uchun ishlatiladi.
"""

import time
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject


class ThrottlingMiddleware(BaseMiddleware):
    """
    Har bir foydalanuvchi uchun so'rovlar orasidagi minimal vaqtni
    nazorat qiladigan middleware.

    Agar foydalanuvchi belgilangan vaqt oralig'ida (default: 0.7 soniya)
    qayta so'rov yuborsa, bu so'rov e'tiborsiz qoldiriladi.
    """

    def __init__(self, rate_limit: float = 0.7):
        """
        Args:
            rate_limit: Ikki so'rov orasidagi minimal ruxsat etilgan
                vaqt (soniyalarda).
        """
        self.rate_limit = rate_limit
        self._last_request: Dict[int, float] = {}
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user_id = self._extract_user_id(event)

        if user_id is not None:
            current_time = time.monotonic()
            last_time = self._last_request.get(user_id)

            if last_time is not None and (current_time - last_time) < self.rate_limit:
                # Foydalanuvchi juda tez so'rov yubordi — e'tiborsiz qoldiramiz
                if isinstance(event, CallbackQuery):
                    await event.answer(
                        "⏳ Iltimos, biroz kuting...", show_alert=False
                    )
                return None

            self._last_request[user_id] = current_time

        return await handler(event, data)

    @staticmethod
    def _extract_user_id(event: TelegramObject):
        """Message yoki CallbackQuery obyektidan foydalanuvchi ID sini oladi."""
        if isinstance(event, Message) and event.from_user:
            return event.from_user.id
        if isinstance(event, CallbackQuery) and event.from_user:
            return event.from_user.id
        return None

# 📁 JOYLASHUV: aggressor_uc_bot/middlewares/antispam.py
# ⚠ YANGI FAYL
"""
AGGRESSOR UC BOT - Anti Spam middleware.

Mavjud `middlewares/throttling.py` dan farqli o'laroq, bu middleware
belgilangan vaqt oynasida juda ko'p so'rov yuborgan foydalanuvchini
vaqtincha (masalan, 30 soniyaga) butunlay cheklaydi.
"""

import time
from typing import Any, Awaitable, Callable, Dict, List, Optional

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from utils.texts_new import ANTI_SPAM_TEMP_RESTRICTED


class AntiSpamMiddleware(BaseMiddleware):
    """
    Belgilangan vaqt oynasida (`window_seconds`) `max_requests` dan ko'p
    so'rov yuborgan foydalanuvchini `restrict_seconds` davomida cheklaydi.
    """

    def __init__(
        self,
        window_seconds: float = 3.0,
        max_requests: int = 6,
        restrict_seconds: int = 30,
    ):
        self.window_seconds = window_seconds
        self.max_requests = max_requests
        self.restrict_seconds = restrict_seconds
        self._request_log: Dict[int, List[float]] = {}
        self._restricted_until: Dict[int, float] = {}
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user_id = self._extract_user_id(event)
        if user_id is None:
            return await handler(event, data)

        now = time.monotonic()

        restricted_until = self._restricted_until.get(user_id)
        if restricted_until and now < restricted_until:
            remaining = int(restricted_until - now)
            await self._notify(event, remaining)
            return None

        log = self._request_log.setdefault(user_id, [])
        log.append(now)
        self._request_log[user_id] = [t for t in log if now - t <= self.window_seconds]

        if len(self._request_log[user_id]) > self.max_requests:
            self._restricted_until[user_id] = now + self.restrict_seconds
            self._request_log[user_id] = []
            await self._notify(event, self.restrict_seconds)
            return None

        return await handler(event, data)

    @staticmethod
    async def _notify(event: TelegramObject, seconds: int) -> None:
        """Foydalanuvchiga vaqtincha cheklanganini xabar qiladi."""
        text = ANTI_SPAM_TEMP_RESTRICTED.format(seconds=seconds)
        if isinstance(event, CallbackQuery):
            await event.answer(text, show_alert=True)
        elif isinstance(event, Message):
            await event.answer(text)

    @staticmethod
    def _extract_user_id(event: TelegramObject) -> Optional[int]:
        """Message yoki CallbackQuery obyektidan foydalanuvchi ID sini oladi."""
        if isinstance(event, Message) and event.from_user:
            return event.from_user.id
        if isinstance(event, CallbackQuery) and event.from_user:
            return event.from_user.id
        return None

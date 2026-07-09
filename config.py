"""
AGGRESSOR UC BOT - Konfiguratsiya moduli.

Bu modul .env faylidan barcha muhim sozlamalarni o'qib,
butun loyiha bo'ylab foydalanish uchun tayyor obyektlar sifatida taqdim etadi.
"""

import os
import sys
from dataclasses import dataclass, field
from typing import List

from dotenv import load_dotenv

# .env faylini yuklash
load_dotenv()


def _get_env(key: str, default: str = None, required: bool = True) -> str:
    """
    Environment o'zgaruvchisini xavfsiz tarzda o'qiydi.

    Agar majburiy o'zgaruvchi topilmasa, dastur ishga tushmasdan
    aniq xatolik xabari bilan to'xtaydi.
    """
    value = os.getenv(key, default)
    if required and (value is None or value.strip() == ""):
        print(f"[XATOLIK] .env faylida '{key}' o'zgaruvchisi topilmadi yoki bo'sh!")
        sys.exit(1)
    return value


def _parse_admin_ids(raw_value: str) -> List[int]:
    """
    'ADMIN_IDS' qatorini vergul bilan ajratilgan holatdan
    butun sonlar ro'yxatiga aylantiradi.

    Masalan: "123456789,987654321" -> [123456789, 987654321]
    """
    if not raw_value:
        return []

    admin_ids: List[int] = []
    for part in raw_value.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            admin_ids.append(int(part))
        except ValueError:
            print(f"[OGOHLANTIRISH] ADMIN_IDS ichida noto'g'ri qiymat: '{part}' — o'tkazib yuborildi.")
    return admin_ids


@dataclass(frozen=True)
class Config:
    """Butun loyiha bo'ylab ishlatiladigan konfiguratsiya obyekti."""

    # Bot sozlamalari
    BOT_TOKEN: str
    BOT_USERNAME: str

    # Adminlar
    ADMIN_IDS: List[int] = field(default_factory=list)

    # To'lov ma'lumotlari (default qiymatlar - keyinchalik settings jadvalidan o'zgartirilishi mumkin)
    CARD_NUMBER: str = ""
    CARD_OWNER: str = ""

    # Database
    DATABASE_PATH: str = "data/aggressor_uc.db"

    # Contact ma'lumotlari
    CONTACT_PHONE: str = ""
    CONTACT_USERNAME: str = ""

    # Timezone
    TIMEZONE: str = "Asia/Tashkent"

    def is_admin(self, user_id: int) -> bool:
        """Berilgan Telegram ID admin ekanligini tekshiradi."""
        return user_id in self.ADMIN_IDS


def load_config() -> Config:
    """
    .env faylidan barcha sozlamalarni o'qib, Config obyektini yaratadi.

    Returns:
        Config: To'ldirilgan konfiguratsiya obyekti.
    """
    bot_token = _get_env("BOT_TOKEN", required=True)
    bot_username = _get_env("BOT_USERNAME", default="aggressor_uc_bot", required=False)

    raw_admin_ids = _get_env("ADMIN_IDS", required=True)
    admin_ids = _parse_admin_ids(raw_admin_ids)

    if not admin_ids:
        print("[XATOLIK] ADMIN_IDS bo'sh yoki noto'g'ri formatda. "
              "Kamida bitta admin ID kiritilishi shart!")
        sys.exit(1)

    card_number = _get_env("CARD_NUMBER", default="", required=False)
    card_owner = _get_env("CARD_OWNER", default="", required=False)

    database_path = _get_env("DATABASE_PATH", default="data/aggressor_uc.db", required=False)

    contact_phone = _get_env("CONTACT_PHONE", default="", required=False)
    contact_username = _get_env("CONTACT_USERNAME", default="", required=False)

    timezone = _get_env("TIMEZONE", default="Asia/Tashkent", required=False)

    return Config(
        BOT_TOKEN=bot_token,
        BOT_USERNAME=bot_username,
        ADMIN_IDS=admin_ids,
        CARD_NUMBER=card_number,
        CARD_OWNER=card_owner,
        DATABASE_PATH=database_path,
        CONTACT_PHONE=contact_phone,
        CONTACT_USERNAME=contact_username,
        TIMEZONE=timezone,
    )


# Global konfiguratsiya obyekti - butun loyiha shu yerdan import qiladi
config = load_config()

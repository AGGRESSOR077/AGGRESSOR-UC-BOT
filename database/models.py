"""
AGGRESSOR UC BOT - Database modellari.

Bu modul database jadvallaridagi qatorlarni Python obyektlariga
aylantirish uchun ishlatiladigan dataclass'larni o'z ichiga oladi.
Bu SQL natijalarini kod ichida qulay va o'qilishi oson tarzda
ishlatish imkonini beradi.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    """`users` jadvalidagi bitta foydalanuvchi qatorini ifodalaydi."""

    id: int
    telegram_id: int
    username: Optional[str]
    full_name: Optional[str]
    phone_number: Optional[str]
    created_at: str
    is_blocked: bool = False

    @classmethod
    def from_row(cls, row) -> "User":
        """SQLite qatoridan (sqlite3.Row yoki tuple) User obyektini yaratadi."""
        return cls(
            id=row["id"],
            telegram_id=row["telegram_id"],
            username=row["username"],
            full_name=row["full_name"],
            phone_number=row["phone_number"],
            created_at=row["created_at"],
            is_blocked=bool(row["is_blocked"]),
        )


@dataclass
class Admin:
    """`admins` jadvalidagi bitta admin qatorini ifodalaydi."""

    id: int
    telegram_id: int
    full_name: Optional[str]
    added_at: str

    @classmethod
    def from_row(cls, row) -> "Admin":
        """SQLite qatoridan Admin obyektini yaratadi."""
        return cls(
            id=row["id"],
            telegram_id=row["telegram_id"],
            full_name=row["full_name"],
            added_at=row["added_at"],
        )


@dataclass
class Package:
    """`packages` jadvalidagi bitta UC paketini ifodalaydi."""

    id: int
    name: str
    uc_amount: int
    price: float
    is_active: bool = True
    created_at: Optional[str] = None

    @classmethod
    def from_row(cls, row) -> "Package":
        """SQLite qatoridan Package obyektini yaratadi."""
        return cls(
            id=row["id"],
            name=row["name"],
            uc_amount=row["uc_amount"],
            price=row["price"],
            is_active=bool(row["is_active"]),
            created_at=row["created_at"],
        )

    def display_name(self) -> str:
        """Foydalanuvchiga ko'rsatish uchun formatlangan nom qaytaradi."""
        return f"{self.uc_amount} UC — {self.name}"

    def display_price(self) -> str:
        """Narxni formatlangan holda qaytaradi (masalan: 150 000 so'm)."""
        return f"{self.price:,.0f} so'm".replace(",", " ")


@dataclass
class Order:
    """`orders` jadvalidagi bitta buyurtmani ifodalaydi."""

    id: int
    user_id: int
    telegram_id: int
    username: Optional[str]
    pubg_uid: str
    package_id: int
    package_name: str
    uc_amount: int
    price: float
    receipt_photo_id: Optional[str]
    status: str  # "pending", "confirmed", "cancelled", "completed"
    created_at: str
    updated_at: Optional[str] = None

    @classmethod
    def from_row(cls, row) -> "Order":
        """SQLite qatoridan Order obyektini yaratadi."""
        return cls(
            id=row["id"],
            user_id=row["user_id"],
            telegram_id=row["telegram_id"],
            username=row["username"],
            pubg_uid=row["pubg_uid"],
            package_id=row["package_id"],
            package_name=row["package_name"],
            uc_amount=row["uc_amount"],
            price=row["price"],
            receipt_photo_id=row["receipt_photo_id"],
            status=row["status"],
            created_at=row["created_at"],
            updated_at=row["updated_at"] if "updated_at" in row.keys() else None,
        )

    def status_display(self) -> str:
        """Holatni o'zbek tilida chiroyli ko'rinishda qaytaradi."""
        status_map = {
            "pending": "⏳ Kutilmoqda",
            "confirmed": "✅ Tasdiqlangan",
            "cancelled": "❌ Bekor qilingan",
            "completed": "🎮 Bajarilgan",
        }
        return status_map.get(self.status, self.status)

    def display_price(self) -> str:
        """Narxni formatlangan holda qaytaradi."""
        return f"{self.price:,.0f} so'm".replace(",", " ")


@dataclass
class Settings:
    """`settings` jadvalidagi kalit-qiymat sozlamalarini ifodalaydi."""

    key: str
    value: str

    @classmethod
    def from_row(cls, row) -> "Settings":
        """SQLite qatoridan Settings obyektini yaratadi."""
        return cls(
            key=row["key"],
            value=row["value"],
        )


def current_timestamp() -> str:
    """Joriy vaqtni database uchun standart formatda qaytaradi."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

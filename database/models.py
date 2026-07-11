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
    # ---- YANGI: Referral tizimi ----
    referral_code: Optional[str] = None
    referred_by: Optional[int] = None
    # ---- YANGI: Bonus / promo balansi ----
    bonus_balance: float = 0.0
    # ---- YANGI: Tug'ilgan kun (MM-DD formatida) ----
    birthday: Optional[str] = None
    # ---- YANGI: Ban tizimi ----
    is_banned: bool = False
    ban_reason: Optional[str] = None
    banned_at: Optional[str] = None
    # ---- YANGI: Blacklist (ban'dan farqli, faqat cheklov) ----
    is_blacklisted: bool = False

    @classmethod
    def from_row(cls, row) -> "User":
        """SQLite qatoridan (sqlite3.Row yoki tuple) User obyektini yaratadi."""
        keys = row.keys()
        return cls(
            id=row["id"],
            telegram_id=row["telegram_id"],
            username=row["username"],
            full_name=row["full_name"],
            phone_number=row["phone_number"],
            created_at=row["created_at"],
            is_blocked=bool(row["is_blocked"]),
            referral_code=row["referral_code"] if "referral_code" in keys else None,
            referred_by=row["referred_by"] if "referred_by" in keys else None,
            bonus_balance=float(row["bonus_balance"]) if "bonus_balance" in keys and row["bonus_balance"] is not None else 0.0,
            birthday=row["birthday"] if "birthday" in keys else None,
            is_banned=bool(row["is_banned"]) if "is_banned" in keys else False,
            ban_reason=row["ban_reason"] if "ban_reason" in keys else None,
            banned_at=row["banned_at"] if "banned_at" in keys else None,
            is_blacklisted=bool(row["is_blacklisted"]) if "is_blacklisted" in keys else False,
        )

    def display_name(self) -> str:
        """Foydalanuvchini admin ro'yxatlarida ko'rsatish uchun formatlaydi."""
        name = self.full_name or "Noma'lum"
        username_part = f"@{self.username}" if self.username else "username yo'q"
        return f"{name} | {username_part} | ID: {self.telegram_id}"


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
    # ---- YANGI: Buyurtma raqami offseti (#1001, #1002...) ----
    ORDER_NUMBER_OFFSET = 1000
    # ---- YANGI: Reyting (1-5 ⭐, mijoz buyurtma tugagach beradi) ----
    rating: Optional[int] = None
    # ---- YANGI: Qaysi to'lov usuli orqali to'langan ----
    payment_method: Optional[str] = None
    # ---- YANGI: Auto Cancel uchun muddat (chek shu vaqtgacha kutiladi) ----
    expires_at: Optional[str] = None
    # ---- YANGI: AI Check Ready — kelajakda AI chek tekshiruvi uchun ----
    ai_check_status: str = "not_checked"  # not_checked, pending, approved, rejected
    ai_check_note: Optional[str] = None

    @classmethod
    def from_row(cls, row) -> "Order":
        """SQLite qatoridan Order obyektini yaratadi."""
        keys = row.keys()
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
            updated_at=row["updated_at"] if "updated_at" in keys else None,
            rating=row["rating"] if "rating" in keys else None,
            payment_method=row["payment_method"] if "payment_method" in keys else None,
            expires_at=row["expires_at"] if "expires_at" in keys else None,
            ai_check_status=row["ai_check_status"] if "ai_check_status" in keys and row["ai_check_status"] else "not_checked",
            ai_check_note=row["ai_check_note"] if "ai_check_note" in keys else None,
        )

    @property
    def order_number(self) -> str:
        """Foydalanuvchiga ko'rsatiladigan unikal buyurtma raqami (masalan: #1001)."""
        return f"#{self.ORDER_NUMBER_OFFSET + self.id}"

    def status_display(self) -> str:
        """Holatni o'zbek tilida chiroyli ko'rinishda qaytaradi."""
        status_map = {
            "pending": "⏳ Kutilmoqda",
            "confirmed": "✅ Tasdiqlangan",
            "cancelled": "❌ Bekor qilingan",
            "completed": "🎮 Bajarilgan",
        }
        return status_map.get(self.status, self.status)

    def rating_display(self) -> str:
        """Reytingni yulduzcha ko'rinishida qaytaradi."""
        if not self.rating:
            return "Baholanmagan"
        return "⭐" * self.rating

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


# ==========================================================
# YANGI FUNKSIYALAR UCHUN MODELLAR
# ==========================================================


@dataclass
class PromoCode:
    """`promo_codes` jadvalidagi bitta promo kodni ifodalaydi."""

    id: int
    code: str
    promo_type: str  # "percent", "fixed", "free_uc"
    discount_percent: int
    discount_amount: float
    free_uc_amount: int
    max_uses: int
    used_count: int
    is_active: bool
    created_at: str
    expires_at: Optional[str] = None

    @classmethod
    def from_row(cls, row) -> "PromoCode":
        """SQLite qatoridan PromoCode obyektini yaratadi."""
        keys = row.keys()
        return cls(
            id=row["id"],
            code=row["code"],
            promo_type=row["promo_type"] if "promo_type" in keys and row["promo_type"] else "percent",
            discount_percent=row["discount_percent"] or 0,
            discount_amount=row["discount_amount"] if "discount_amount" in keys and row["discount_amount"] else 0.0,
            free_uc_amount=row["free_uc_amount"] if "free_uc_amount" in keys and row["free_uc_amount"] else 0,
            max_uses=row["max_uses"],
            used_count=row["used_count"],
            is_active=bool(row["is_active"]),
            created_at=row["created_at"],
            expires_at=row["expires_at"],
        )

    def is_usable(self) -> bool:
        """Promo kod hali ishlatilishi mumkinligini tekshiradi."""
        if not self.is_active:
            return False
        if self.max_uses > 0 and self.used_count >= self.max_uses:
            return False
        if self.expires_at:
            try:
                expires = datetime.strptime(self.expires_at, "%Y-%m-%d %H:%M:%S")
                if datetime.now() > expires:
                    return False
            except ValueError:
                pass
        return True

    def type_display(self) -> str:
        """Promo turini o'zbek tilida chiroyli ko'rinishda qaytaradi."""
        type_map = {
            "percent": f"Foizli chegirma — {self.discount_percent}%",
            "fixed": f"Belgilangan summa — {self.discount_amount:,.0f} so'm".replace(",", " "),
            "free_uc": f"Bepul UC — {self.free_uc_amount} UC",
        }
        return type_map.get(self.promo_type, self.promo_type)


@dataclass
class Referral:
    """`referrals` jadvalidagi bitta taklif yozuvini ifodalaydi."""

    id: int
    referrer_telegram_id: int
    referred_telegram_id: int
    bonus_amount: float
    created_at: str

    @classmethod
    def from_row(cls, row) -> "Referral":
        """SQLite qatoridan Referral obyektini yaratadi."""
        return cls(
            id=row["id"],
            referrer_telegram_id=row["referrer_telegram_id"],
            referred_telegram_id=row["referred_telegram_id"],
            bonus_amount=row["bonus_amount"],
            created_at=row["created_at"],
        )


@dataclass
class Banner:
    """`banners` jadvalidagi bitta reklama bannerini ifodalaydi."""

    id: int
    text: str
    image_file_id: Optional[str]
    is_active: bool
    created_at: str

    @classmethod
    def from_row(cls, row) -> "Banner":
        """SQLite qatoridan Banner obyektini yaratadi."""
        return cls(
            id=row["id"],
            text=row["text"],
            image_file_id=row["image_file_id"],
            is_active=bool(row["is_active"]),
            created_at=row["created_at"],
        )


@dataclass
class NewsPost:
    """`news` jadvalidagi bitta yangilik/aksiya postini ifodalaydi."""

    id: int
    title: str
    text: str
    image_file_id: Optional[str]
    created_at: str

    @classmethod
    def from_row(cls, row) -> "NewsPost":
        """SQLite qatoridan NewsPost obyektini yaratadi."""
        return cls(
            id=row["id"],
            title=row["title"],
            text=row["text"],
            image_file_id=row["image_file_id"],
            created_at=row["created_at"],
        )


@dataclass
class PaymentMethod:
    """`payment_methods` jadvalidagi bitta to'lov usulini ifodalaydi."""

    id: int
    name: str
    card_number: str
    card_owner: str
    is_active: bool
    created_at: str

    @classmethod
    def from_row(cls, row) -> "PaymentMethod":
        """SQLite qatoridan PaymentMethod obyektini yaratadi."""
        return cls(
            id=row["id"],
            name=row["name"],
            card_number=row["card_number"],
            card_owner=row["card_owner"],
            is_active=bool(row["is_active"]),
            created_at=row["created_at"],
        )

    def display(self) -> str:
        """To'lov usulini chiroyli ko'rinishda qaytaradi."""
        return f"💳 {self.name}: {self.card_number} ({self.card_owner})"


@dataclass
class UserStats:
    """
    Mini CRM uchun bitta foydalanuvchining xarid statistikasini ifodalaydi.

    Bu model database jadvaliga emas, balki `orders` jadvali ustidan
    hisoblangan agregatsiya natijasiga mos keladi.
    """

    orders_count: int
    total_spent: float
    first_order_at: Optional[str]
    last_order_at: Optional[str]

    def total_spent_display(self) -> str:
        """Umumiy xarid summasini formatlangan holda qaytaradi."""
        return f"{self.total_spent:,.0f} so'm".replace(",", " ")


@dataclass
class AdminLog:
    """`admin_logs` jadvalidagi bitta admin amali yozuvini ifodalaydi."""

    id: int
    admin_telegram_id: int
    action: str
    details: Optional[str]
    created_at: str

    @classmethod
    def from_row(cls, row) -> "AdminLog":
        """SQLite qatoridan AdminLog obyektini yaratadi."""
        return cls(
            id=row["id"],
            admin_telegram_id=row["admin_telegram_id"],
            action=row["action"],
            details=row["details"],
            created_at=row["created_at"],
        )

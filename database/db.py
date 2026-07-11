"""
AGGRESSOR UC BOT - Database boshqaruv moduli.

Bu modul SQLite database bilan barcha ishlarni (jadval yaratish,
qo'shish, o'qish, yangilash, o'chirish) amalga oshiradi.
aiosqlite kutubxonasi orqali asinxron tarzda ishlaydi.
"""

import os
from contextlib import asynccontextmanager
from typing import AsyncIterator, List, Optional

import aiosqlite

from database.models import (
    Admin,
    AdminLog,
    Banner,
    NewsPost,
    Order,
    Package,
    PaymentMethod,
    PromoCode,
    Referral,
    Settings,
    User,
    UserStats,
    current_timestamp,
)


class Database:
    """SQLite database bilan ishlash uchun asosiy klass."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        # Database fayli joylashadigan papka mavjudligini ta'minlash
        directory = os.path.dirname(db_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

    @asynccontextmanager
    async def _connect(self) -> AsyncIterator[aiosqlite.Connection]:
        """
        Yangi database ulanishini ochadigan asinxron kontekst menejeri.

        `aiosqlite.connect()` o'zi ham asinxron kontekst menejeri
        bo'lgani uchun, uni ikkinchi marta `async with await ...`
        ko'rinishida ishlatish "threads can only be started once"
        xatosiga olib keladi. Shu sababli bu yerda ulanish ochilib,
        `yield` orqali chaqiruvchiga uzatiladi va `finally` blokida
        albatta yopiladi.
        """
        connection = await aiosqlite.connect(self.db_path)
        connection.row_factory = aiosqlite.Row
        try:
            await connection.execute("PRAGMA foreign_keys = ON;")
            yield connection
        finally:
            await connection.close()

    async def _ensure_column(
        self, conn: aiosqlite.Connection, table: str, column: str, definition: str
    ) -> None:
        """
        Berilgan jadvalda ustun mavjudligini tekshiradi va agar mavjud
        bo'lmasa, uni xavfsiz tarzda qo'shadi (mavjud ma'lumotlarni
        yo'qotmasdan).

        Bu metod database migratsiyasini xavfsiz qiladi: eski
        database fayllarida yangi ustunlar avtomatik paydo bo'ladi,
        mavjud qatorlar esa o'zgarishsiz qoladi.
        """
        cursor = await conn.execute(f"PRAGMA table_info({table})")
        existing_columns = {row["name"] for row in await cursor.fetchall()}
        if column not in existing_columns:
            await conn.execute(f"ALTER TABLE {table} ADD COLUMN {definition}")

    # ==========================================================
    # JADVALLARNI YARATISH
    # ==========================================================

    async def create_tables(self) -> None:
        """Barcha kerakli jadvallarni (agar mavjud bo'lmasa) yaratadi."""
        async with self._connect() as conn:
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER UNIQUE NOT NULL,
                    username TEXT,
                    full_name TEXT,
                    phone_number TEXT,
                    created_at TEXT NOT NULL,
                    is_blocked INTEGER NOT NULL DEFAULT 0
                );
                """
            )

            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS admins (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER UNIQUE NOT NULL,
                    full_name TEXT,
                    added_at TEXT NOT NULL
                );
                """
            )

            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS packages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    uc_amount INTEGER NOT NULL,
                    price REAL NOT NULL,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL
                );
                """
            )

            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    telegram_id INTEGER NOT NULL,
                    username TEXT,
                    pubg_uid TEXT NOT NULL,
                    package_id INTEGER NOT NULL,
                    package_name TEXT NOT NULL,
                    uc_amount INTEGER NOT NULL,
                    price REAL NOT NULL,
                    receipt_photo_id TEXT,
                    status TEXT NOT NULL DEFAULT 'pending',
                    created_at TEXT NOT NULL,
                    updated_at TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (package_id) REFERENCES packages (id)
                );
                """
            )

            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                );
                """
            )

            # ---- YANGI: users jadvaliga xavfsiz ustun qo'shish ----
            await self._ensure_column(conn, "users", "referral_code", "referral_code TEXT")
            await self._ensure_column(conn, "users", "referred_by", "referred_by INTEGER")
            await self._ensure_column(conn, "users", "bonus_balance", "bonus_balance REAL NOT NULL DEFAULT 0")
            await self._ensure_column(conn, "users", "birthday", "birthday TEXT")
            await self._ensure_column(conn, "users", "is_banned", "is_banned INTEGER NOT NULL DEFAULT 0")
            await self._ensure_column(conn, "users", "ban_reason", "ban_reason TEXT")
            await self._ensure_column(conn, "users", "banned_at", "banned_at TEXT")
            await self._ensure_column(conn, "users", "is_blacklisted", "is_blacklisted INTEGER NOT NULL DEFAULT 0")

            # ---- YANGI: orders jadvaliga xavfsiz ustun qo'shish ----
            await self._ensure_column(conn, "orders", "rating", "rating INTEGER")
            await self._ensure_column(conn, "orders", "payment_method", "payment_method TEXT")
            await self._ensure_column(conn, "orders", "expires_at", "expires_at TEXT")
            await self._ensure_column(
                conn, "orders", "ai_check_status", "ai_check_status TEXT NOT NULL DEFAULT 'not_checked'"
            )
            await self._ensure_column(conn, "orders", "ai_check_note", "ai_check_note TEXT")

            # ---- YANGI: Promo kodlar jadvali ----
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS promo_codes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT UNIQUE NOT NULL,
                    promo_type TEXT NOT NULL DEFAULT 'percent',
                    discount_percent INTEGER NOT NULL DEFAULT 0,
                    discount_amount REAL NOT NULL DEFAULT 0,
                    free_uc_amount INTEGER NOT NULL DEFAULT 0,
                    max_uses INTEGER NOT NULL DEFAULT 0,
                    used_count INTEGER NOT NULL DEFAULT 0,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL,
                    expires_at TEXT
                );
                """
            )

            # ---- YANGI: Promo kod ishlatilishi tarixi (bir marta ishlatish uchun) ----
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS promo_code_usages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    promo_id INTEGER NOT NULL,
                    telegram_id INTEGER NOT NULL,
                    order_id INTEGER,
                    used_at TEXT NOT NULL,
                    FOREIGN KEY (promo_id) REFERENCES promo_codes (id)
                );
                """
            )

            # ---- YANGI: Referral tizimi jadvali ----
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS referrals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    referrer_telegram_id INTEGER NOT NULL,
                    referred_telegram_id INTEGER UNIQUE NOT NULL,
                    bonus_amount REAL NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL
                );
                """
            )

            # ---- YANGI: Banner (reklama/aksiya) jadvali ----
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS banners (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT NOT NULL,
                    image_file_id TEXT,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL
                );
                """
            )

            # ---- YANGI: Yangiliklar / aksiyalar jadvali ----
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS news (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    text TEXT NOT NULL,
                    image_file_id TEXT,
                    created_at TEXT NOT NULL
                );
                """
            )

            # ---- YANGI: Bir nechta to'lov usullari jadvali ----
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS payment_methods (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    card_number TEXT NOT NULL,
                    card_owner TEXT NOT NULL,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL
                );
                """
            )

            # ---- YANGI: Admin amallari logi ----
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS admin_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    admin_telegram_id INTEGER NOT NULL,
                    action TEXT NOT NULL,
                    details TEXT,
                    created_at TEXT NOT NULL
                );
                """
            )

            await conn.commit()

    # ==========================================================
    # USERS
    # ==========================================================

    async def add_user(
        self,
        telegram_id: int,
        username: Optional[str],
        full_name: Optional[str],
        phone_number: Optional[str] = None,
    ) -> None:
        """Yangi foydalanuvchini qo'shadi. Agar mavjud bo'lsa, hech narsa qilmaydi."""
        async with self._connect() as conn:
            existing = await conn.execute(
                "SELECT id FROM users WHERE telegram_id = ?", (telegram_id,)
            )
            row = await existing.fetchone()
            if row:
                # Mavjud foydalanuvchining username/full_name'ini yangilab qo'yamiz
                await conn.execute(
                    """
                    UPDATE users
                    SET username = ?, full_name = ?
                    WHERE telegram_id = ?
                    """,
                    (username, full_name, telegram_id),
                )
                await conn.commit()
                return

            await conn.execute(
                """
                INSERT INTO users (telegram_id, username, full_name, phone_number, created_at, is_blocked)
                VALUES (?, ?, ?, ?, ?, 0)
                """,
                (telegram_id, username, full_name, phone_number, current_timestamp()),
            )
            await conn.commit()

    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Telegram ID orqali foydalanuvchini qaytaradi."""
        async with self._connect() as conn:
            cursor = await conn.execute(
                "SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)
            )
            row = await cursor.fetchone()
            return User.from_row(row) if row else None

    async def get_all_users(self) -> List[User]:
        """Barcha foydalanuvchilar ro'yxatini qaytaradi."""
        async with self._connect() as conn:
            cursor = await conn.execute("SELECT * FROM users ORDER BY id DESC")
            rows = await cursor.fetchall()
            return [User.from_row(row) for row in rows]

    async def get_all_user_telegram_ids(self, only_active: bool = True) -> List[int]:
        """Broadcast uchun barcha foydalanuvchilarning Telegram ID larini qaytaradi."""
        async with self._connect() as conn:
            query = "SELECT telegram_id FROM users"
            if only_active:
                query += " WHERE is_blocked = 0"
            cursor = await conn.execute(query)
            rows = await cursor.fetchall()
            return [row["telegram_id"] for row in rows]

    async def count_users(self) -> int:
        """Jami foydalanuvchilar sonini qaytaradi."""
        async with self._connect() as conn:
            cursor = await conn.execute("SELECT COUNT(*) as cnt FROM users")
            row = await cursor.fetchone()
            return row["cnt"] if row else 0

    async def block_user(self, telegram_id: int) -> None:
        """Foydalanuvchini bloklaydi."""
        async with self._connect() as conn:
            await conn.execute(
                "UPDATE users SET is_blocked = 1 WHERE telegram_id = ?", (telegram_id,)
            )
            await conn.commit()

    async def unblock_user(self, telegram_id: int) -> None:
        """Foydalanuvchi blokini bekor qiladi."""
        async with self._connect() as conn:
            await conn.execute(
                "UPDATE users SET is_blocked = 0 WHERE telegram_id = ?", (telegram_id,)
            )
            await conn.commit()

    # ---- YANGI: Ban tizimi ----

    async def ban_user(self, telegram_id: int, reason: str) -> None:
        """Foydalanuvchini sabab bilan ban qiladi."""
        async with self._connect() as conn:
            await conn.execute(
                """
                UPDATE users
                SET is_banned = 1, ban_reason = ?, banned_at = ?
                WHERE telegram_id = ?
                """,
                (reason, current_timestamp(), telegram_id),
            )
            await conn.commit()

    async def unban_user(self, telegram_id: int) -> None:
        """Foydalanuvchini bandan chiqaradi."""
        async with self._connect() as conn:
            await conn.execute(
                """
                UPDATE users
                SET is_banned = 0, ban_reason = NULL, banned_at = NULL
                WHERE telegram_id = ?
                """,
                (telegram_id,),
            )
            await conn.commit()

    # ---- YANGI: Blacklist ----

    async def add_to_blacklist(self, telegram_id: int) -> None:
        """Foydalanuvchini qora ro'yxatga qo'shadi."""
        async with self._connect() as conn:
            await conn.execute(
                "UPDATE users SET is_blacklisted = 1 WHERE telegram_id = ?", (telegram_id,)
            )
            await conn.commit()

    async def remove_from_blacklist(self, telegram_id: int) -> None:
        """Foydalanuvchini qora ro'yxatdan chiqaradi."""
        async with self._connect() as conn:
            await conn.execute(
                "UPDATE users SET is_blacklisted = 0 WHERE telegram_id = ?", (telegram_id,)
            )
            await conn.commit()

    # ---- YANGI: Referral tizimi ----

    async def set_user_referral_code(self, telegram_id: int, referral_code: str) -> None:
        """Foydalanuvchiga unikal referral kod biriktiradi."""
        async with self._connect() as conn:
            await conn.execute(
                "UPDATE users SET referral_code = ? WHERE telegram_id = ?",
                (referral_code, telegram_id),
            )
            await conn.commit()

    async def get_user_by_referral_code(self, referral_code: str) -> Optional[User]:
        """Referral kod orqali foydalanuvchini topadi."""
        async with self._connect() as conn:
            cursor = await conn.execute(
                "SELECT * FROM users WHERE referral_code = ?", (referral_code,)
            )
            row = await cursor.fetchone()
            return User.from_row(row) if row else None

    async def set_user_referred_by(self, telegram_id: int, referrer_telegram_id: int) -> None:
        """Foydalanuvchini kim taklif qilganini belgilaydi."""
        async with self._connect() as conn:
            await conn.execute(
                "UPDATE users SET referred_by = ? WHERE telegram_id = ?",
                (referrer_telegram_id, telegram_id),
            )
            await conn.commit()

    async def increase_bonus_balance(self, telegram_id: int, amount: float) -> None:
        """Foydalanuvchi bonus balansini oshiradi."""
        async with self._connect() as conn:
            await conn.execute(
                "UPDATE users SET bonus_balance = bonus_balance + ? WHERE telegram_id = ?",
                (amount, telegram_id),
            )
            await conn.commit()

    async def set_user_birthday(self, telegram_id: int, birthday: str) -> None:
        """Foydalanuvchi tug'ilgan kunini saqlaydi (MM-DD formatida)."""
        async with self._connect() as conn:
            await conn.execute(
                "UPDATE users SET birthday = ? WHERE telegram_id = ?",
                (birthday, telegram_id),
            )
            await conn.commit()

    async def get_users_with_birthday_today(self) -> List[User]:
        """Bugun tug'ilgan kuni bo'lgan foydalanuvchilarni qaytaradi."""
        async with self._connect() as conn:
            cursor = await conn.execute(
                """
                SELECT * FROM users
                WHERE birthday IS NOT NULL
                AND strftime('%m-%d', birthday) = strftime('%m-%d', 'now', 'localtime')
                """
            )
            rows = await cursor.fetchall()
            return [User.from_row(row) for row in rows]

    # ---- YANGI: Pagination bilan foydalanuvchilar ro'yxati ----

    async def get_users_paginated(self, page: int, page_size: int = 10) -> List[User]:
        """
        Foydalanuvchilarni sahifalab (pagination) qaytaradi.

        Args:
            page: Sahifa raqami (1 dan boshlanadi).
            page_size: Har sahifadagi foydalanuvchilar soni.
        """
        offset = (page - 1) * page_size
        async with self._connect() as conn:
            cursor = await conn.execute(
                "SELECT * FROM users ORDER BY id DESC LIMIT ? OFFSET ?",
                (page_size, offset),
            )
            rows = await cursor.fetchall()
            return [User.from_row(row) for row in rows]

    async def get_users_total_pages(self, page_size: int = 10) -> int:
        """Foydalanuvchilar ro'yxati uchun jami sahifalar sonini hisoblaydi."""
        total = await self.count_users()
        if total == 0:
            return 1
        return (total + page_size - 1) // page_size

    # ==========================================================
    # ADMINS
    # ==========================================================

    async def add_admin(self, telegram_id: int, full_name: Optional[str] = None) -> None:
        """Yangi adminni qo'shadi (agar mavjud bo'lmasa)."""
        async with self._connect() as conn:
            cursor = await conn.execute(
                "SELECT id FROM admins WHERE telegram_id = ?", (telegram_id,)
            )
            row = await cursor.fetchone()
            if row:
                return

            await conn.execute(
                """
                INSERT INTO admins (telegram_id, full_name, added_at)
                VALUES (?, ?, ?)
                """,
                (telegram_id, full_name, current_timestamp()),
            )
            await conn.commit()

    async def get_all_admins(self) -> List[Admin]:
        """Barcha adminlar ro'yxatini qaytaradi."""
        async with self._connect() as conn:
            cursor = await conn.execute("SELECT * FROM admins ORDER BY id ASC")
            rows = await cursor.fetchall()
            return [Admin.from_row(row) for row in rows]

    async def is_admin_in_db(self, telegram_id: int) -> bool:
        """Berilgan Telegram ID admins jadvalida mavjudligini tekshiradi."""
        async with self._connect() as conn:
            cursor = await conn.execute(
                "SELECT id FROM admins WHERE telegram_id = ?", (telegram_id,)
            )
            row = await cursor.fetchone()
            return row is not None

    # ==========================================================
    # PACKAGES
    # ==========================================================

    async def add_package(self, name: str, uc_amount: int, price: float) -> int:
        """Yangi UC paketini qo'shadi va yaratilgan paket ID sini qaytaradi."""
        async with self._connect() as conn:
            cursor = await conn.execute(
                """
                INSERT INTO packages (name, uc_amount, price, is_active, created_at)
                VALUES (?, ?, ?, 1, ?)
                """,
                (name, uc_amount, price, current_timestamp()),
            )
            await conn.commit()
            return cursor.lastrowid

    async def get_package(self, package_id: int) -> Optional[Package]:
        """ID orqali bitta paketni qaytaradi."""
        async with self._connect() as conn:
            cursor = await conn.execute(
                "SELECT * FROM packages WHERE id = ?", (package_id,)
            )
            row = await cursor.fetchone()
            return Package.from_row(row) if row else None

    async def get_all_packages(self, only_active: bool = False) -> List[Package]:
        """Barcha paketlar ro'yxatini qaytaradi."""
        async with self._connect() as conn:
            query = "SELECT * FROM packages"
            if only_active:
                query += " WHERE is_active = 1"
            query += " ORDER BY uc_amount ASC"
            cursor = await conn.execute(query)
            rows = await cursor.fetchall()
            return [Package.from_row(row) for row in rows]

    async def update_package(
        self,
        package_id: int,
        name: Optional[str] = None,
        uc_amount: Optional[int] = None,
        price: Optional[float] = None,
    ) -> None:
        """Mavjud paket ma'lumotlarini yangilaydi (faqat berilgan maydonlarni)."""
        package = await self.get_package(package_id)
        if not package:
            return

        new_name = name if name is not None else package.name
        new_uc_amount = uc_amount if uc_amount is not None else package.uc_amount
        new_price = price if price is not None else package.price

        async with self._connect() as conn:
            await conn.execute(
                """
                UPDATE packages
                SET name = ?, uc_amount = ?, price = ?
                WHERE id = ?
                """,
                (new_name, new_uc_amount, new_price, package_id),
            )
            await conn.commit()

    async def set_package_active(self, package_id: int, is_active: bool) -> None:
        """Paketni faol/nofaol holatga o'tkazadi."""
        async with self._connect() as conn:
            await conn.execute(
                "UPDATE packages SET is_active = ? WHERE id = ?",
                (1 if is_active else 0, package_id),
            )
            await conn.commit()

    async def delete_package(self, package_id: int) -> None:
        """Paketni database'dan butunlay o'chiradi."""
        async with self._connect() as conn:
            await conn.execute("DELETE FROM packages WHERE id = ?", (package_id,))
            await conn.commit()

    # ==========================================================
    # ORDERS
    # ==========================================================

    async def create_order(
        self,
        user_id: int,
        telegram_id: int,
        username: Optional[str],
        pubg_uid: str,
        package_id: int,
        package_name: str,
        uc_amount: int,
        price: float,
        receipt_photo_id: Optional[str] = None,
    ) -> int:
        """Yangi buyurtma yaratadi va uning ID sini qaytaradi."""
        async with self._connect() as conn:
            cursor = await conn.execute(
                """
                INSERT INTO orders (
                    user_id, telegram_id, username, pubg_uid,
                    package_id, package_name, uc_amount, price,
                    receipt_photo_id, status, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?)
                """,
                (
                    user_id,
                    telegram_id,
                    username,
                    pubg_uid,
                    package_id,
                    package_name,
                    uc_amount,
                    price,
                    receipt_photo_id,
                    current_timestamp(),
                ),
            )
            await conn.commit()
            return cursor.lastrowid

    async def get_order(self, order_id: int) -> Optional[Order]:
        """ID orqali bitta buyurtmani qaytaradi."""
        async with self._connect() as conn:
            cursor = await conn.execute(
                "SELECT * FROM orders WHERE id = ?", (order_id,)
            )
            row = await cursor.fetchone()
            return Order.from_row(row) if row else None

    async def get_all_orders(self) -> List[Order]:
        """Barcha buyurtmalar ro'yxatini (yangi birinchi) qaytaradi."""
        async with self._connect() as conn:
            cursor = await conn.execute("SELECT * FROM orders ORDER BY id DESC")
            rows = await cursor.fetchall()
            return [Order.from_row(row) for row in rows]

    async def get_orders_by_status(self, status: str) -> List[Order]:
        """Berilgan holatdagi barcha buyurtmalarni qaytaradi."""
        async with self._connect() as conn:
            cursor = await conn.execute(
                "SELECT * FROM orders WHERE status = ? ORDER BY id DESC", (status,)
            )
            rows = await cursor.fetchall()
            return [Order.from_row(row) for row in rows]

    async def get_orders_by_user(self, telegram_id: int) -> List[Order]:
        """Bitta foydalanuvchining barcha buyurtmalarini qaytaradi."""
        async with self._connect() as conn:
            cursor = await conn.execute(
                "SELECT * FROM orders WHERE telegram_id = ? ORDER BY id DESC",
                (telegram_id,),
            )
            rows = await cursor.fetchall()
            return [Order.from_row(row) for row in rows]

    async def update_order_status(self, order_id: int, status: str) -> None:
        """Buyurtma holatini yangilaydi (pending/confirmed/cancelled/completed)."""
        async with self._connect() as conn:
            await conn.execute(
                """
                UPDATE orders
                SET status = ?, updated_at = ?
                WHERE id = ?
                """,
                (status, current_timestamp(), order_id),
            )
            await conn.commit()

    async def set_order_receipt(self, order_id: int, receipt_photo_id: str) -> None:
        """Buyurtmaga chek rasmi ID sini biriktiradi."""
        async with self._connect() as conn:
            await conn.execute(
                "UPDATE orders SET receipt_photo_id = ? WHERE id = ?",
                (receipt_photo_id, order_id),
            )
            await conn.commit()

    # ---- YANGI: Buyurtma ID orqali topish (#1001 ko'rinishidagi raqam) ----

    async def get_order_by_number(self, order_number: int) -> Optional[Order]:
        """
        Foydalanuvchiga ko'rinadigan buyurtma raqami (masalan 1001)
        orqali buyurtmani topadi. Ichki `id` = order_number - OFFSET.
        """
        internal_id = order_number - Order.ORDER_NUMBER_OFFSET
        if internal_id <= 0:
            return None
        return await self.get_order(internal_id)

    # ---- YANGI: Reyting (1-5 ⭐) ----

    async def set_order_rating(self, order_id: int, rating: int) -> None:
        """Buyurtmaga foydalanuvchi bergan reytingni saqlaydi."""
        async with self._connect() as conn:
            await conn.execute(
                "UPDATE orders SET rating = ? WHERE id = ?", (rating, order_id)
            )
            await conn.commit()

    # ---- YANGI: To'lov usuli ----

    async def set_order_payment_method(self, order_id: int, payment_method: str) -> None:
        """Buyurtmaga qaysi to'lov usuli orqali to'langanini biriktiradi."""
        async with self._connect() as conn:
            await conn.execute(
                "UPDATE orders SET payment_method = ? WHERE id = ?",
                (payment_method, order_id),
            )
            await conn.commit()

    # ---- YANGI: Auto Cancel uchun muddat boshqaruvi ----

    async def set_order_expiry(self, order_id: int, expires_at: str) -> None:
        """Buyurtma uchun chek yuborish muddatini belgilaydi."""
        async with self._connect() as conn:
            await conn.execute(
                "UPDATE orders SET expires_at = ? WHERE id = ?",
                (expires_at, order_id),
            )
            await conn.commit()

    async def get_expired_pending_orders(self) -> List[Order]:
        """
        Muddati o'tgan, hali "pending" holatida qolgan buyurtmalarni
        qaytaradi (Auto Cancel job shu ro'yxatni bekor qilish uchun ishlatadi).
        """
        async with self._connect() as conn:
            cursor = await conn.execute(
                """
                SELECT * FROM orders
                WHERE status = 'pending'
                AND expires_at IS NOT NULL
                AND datetime(expires_at) < datetime('now', 'localtime')
                """
            )
            rows = await cursor.fetchall()
            return [Order.from_row(row) for row in rows]

    # ---- YANGI: AI Check Ready ----

    async def set_order_ai_check(self, order_id: int, status: str, note: Optional[str] = None) -> None:
        """
        Buyurtmaning AI orqali chek tekshiruvi natijasini saqlaydi.

        status: "not_checked", "pending", "approved", "rejected"
        Bu metod hozircha handlerlarda chaqirilmaydi, lekin kelajakda
        AI Check integratsiyasi uchun tayyor struktura sifatida mavjud.
        """
        async with self._connect() as conn:
            await conn.execute(
                "UPDATE orders SET ai_check_status = ?, ai_check_note = ? WHERE id = ?",
                (status, note, order_id),
            )
            await conn.commit()

    # ==========================================================
    # STATISTIKA
    # ==========================================================

    async def get_today_income(self) -> float:
        """Bugungi kun uchun tasdiqlangan/bajarilgan buyurtmalar daromadini qaytaradi."""
        async with self._connect() as conn:
            cursor = await conn.execute(
                """
                SELECT COALESCE(SUM(price), 0) as total
                FROM orders
                WHERE status IN ('confirmed', 'completed')
                AND date(created_at) = date('now', 'localtime')
                """
            )
            row = await cursor.fetchone()
            return float(row["total"]) if row else 0.0

    async def get_today_orders_count(self) -> int:
        """Bugun tushgan buyurtmalar sonini qaytaradi (barcha holatlar)."""
        async with self._connect() as conn:
            cursor = await conn.execute(
                """
                SELECT COUNT(*) as cnt
                FROM orders
                WHERE date(created_at) = date('now', 'localtime')
                """
            )
            row = await cursor.fetchone()
            return row["cnt"] if row else 0

    async def get_total_income(self) -> float:
        """Barcha vaqt uchun tasdiqlangan/bajarilgan buyurtmalar jami daromadini qaytaradi."""
        async with self._connect() as conn:
            cursor = await conn.execute(
                """
                SELECT COALESCE(SUM(price), 0) as total
                FROM orders
                WHERE status IN ('confirmed', 'completed')
                """
            )
            row = await cursor.fetchone()
            return float(row["total"]) if row else 0.0

    async def get_total_orders_count(self) -> int:
        """Barcha vaqt uchun jami buyurtmalar sonini qaytaradi."""
        async with self._connect() as conn:
            cursor = await conn.execute("SELECT COUNT(*) as cnt FROM orders")
            row = await cursor.fetchone()
            return row["cnt"] if row else 0

    # ---- YANGI: Kengaytirilgan statistika ----

    async def get_top_buyers(self, limit: int = 5) -> List[dict]:
        """
        Eng ko'p xarid qilgan foydalanuvchilarni qaytaradi.

        Har bir element: {"telegram_id", "username", "full_name",
        "orders_count", "total_spent"}
        """
        async with self._connect() as conn:
            cursor = await conn.execute(
                """
                SELECT
                    telegram_id,
                    username,
                    COUNT(*) as orders_count,
                    COALESCE(SUM(price), 0) as total_spent
                FROM orders
                WHERE status IN ('confirmed', 'completed')
                GROUP BY telegram_id
                ORDER BY total_spent DESC
                LIMIT ?
                """,
                (limit,),
            )
            rows = await cursor.fetchall()
            return [
                {
                    "telegram_id": row["telegram_id"],
                    "username": row["username"],
                    "orders_count": row["orders_count"],
                    "total_spent": row["total_spent"],
                }
                for row in rows
            ]

    async def get_top_selling_packages(self, limit: int = 5) -> List[dict]:
        """
        Eng ko'p sotilgan UC paketlarini qaytaradi.

        Har bir element: {"package_name", "sold_count", "total_income"}
        """
        async with self._connect() as conn:
            cursor = await conn.execute(
                """
                SELECT
                    package_name,
                    COUNT(*) as sold_count,
                    COALESCE(SUM(price), 0) as total_income
                FROM orders
                WHERE status IN ('confirmed', 'completed')
                GROUP BY package_name
                ORDER BY sold_count DESC
                LIMIT ?
                """,
                (limit,),
            )
            rows = await cursor.fetchall()
            return [
                {
                    "package_name": row["package_name"],
                    "sold_count": row["sold_count"],
                    "total_income": row["total_income"],
                }
                for row in rows
            ]

    # ==========================================================
    # SETTINGS
    # ==========================================================

    async def get_setting(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Berilgan kalit bo'yicha sozlama qiymatini qaytaradi."""
        async with self._connect() as conn:
            cursor = await conn.execute(
                "SELECT value FROM settings WHERE key = ?", (key,)
            )
            row = await cursor.fetchone()
            return row["value"] if row else default

    async def set_setting(self, key: str, value: str) -> None:
        """Sozlama qiymatini o'rnatadi yoki yangilaydi."""
        async with self._connect() as conn:
            await conn.execute(
                """
                INSERT INTO settings (key, value)
                VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
                """,
                (key, value),
            )
            await conn.commit()

    async def get_all_settings(self) -> List[Settings]:
        """Barcha sozlamalar ro'yxatini qaytaradi."""
        async with self._connect() as conn:
            cursor = await conn.execute("SELECT * FROM settings")
            rows = await cursor.fetchall()
            return [Settings.from_row(row) for row in rows]

    # ==========================================================
    # YANGI: MINI CRM
    # ==========================================================

    async def get_user_stats(self, telegram_id: int) -> UserStats:
        """
        Foydalanuvchining xarid statistikasini (Mini CRM) qaytaradi:
        buyurtmalar soni, umumiy xarid, birinchi va oxirgi buyurtma sanasi.
        """
        async with self._connect() as conn:
            cursor = await conn.execute(
                """
                SELECT
                    COUNT(*) as orders_count,
                    COALESCE(SUM(CASE WHEN status IN ('confirmed', 'completed') THEN price ELSE 0 END), 0) as total_spent,
                    MIN(created_at) as first_order_at,
                    MAX(created_at) as last_order_at
                FROM orders
                WHERE telegram_id = ?
                """,
                (telegram_id,),
            )
            row = await cursor.fetchone()
            return UserStats(
                orders_count=row["orders_count"] or 0,
                total_spent=float(row["total_spent"] or 0),
                first_order_at=row["first_order_at"],
                last_order_at=row["last_order_at"],
            )

    # ==========================================================
    # YANGI: PROMO KODLAR
    # ==========================================================

    async def add_promo_code(
        self,
        code: str,
        promo_type: str,
        discount_percent: int = 0,
        discount_amount: float = 0.0,
        free_uc_amount: int = 0,
        max_uses: int = 0,
        expires_at: Optional[str] = None,
    ) -> int:
        """Yangi promo kod yaratadi va uning ID sini qaytaradi."""
        async with self._connect() as conn:
            cursor = await conn.execute(
                """
                INSERT INTO promo_codes (
                    code, promo_type, discount_percent, discount_amount,
                    free_uc_amount, max_uses, used_count, is_active,
                    created_at, expires_at
                )
                VALUES (?, ?, ?, ?, ?, ?, 0, 1, ?, ?)
                """,
                (
                    code,
                    promo_type,
                    discount_percent,
                    discount_amount,
                    free_uc_amount,
                    max_uses,
                    current_timestamp(),
                    expires_at,
                ),
            )
            await conn.commit()
            return cursor.lastrowid

    async def get_promo_code(self, promo_id: int) -> Optional[PromoCode]:
        """ID orqali bitta promo kodni qaytaradi."""
        async with self._connect() as conn:
            cursor = await conn.execute(
                "SELECT * FROM promo_codes WHERE id = ?", (promo_id,)
            )
            row = await cursor.fetchone()
            return PromoCode.from_row(row) if row else None

    async def get_promo_code_by_code(self, code: str) -> Optional[PromoCode]:
        """Kod matni orqali promo kodni qaytaradi (foydalanuvchi kiritganda)."""
        async with self._connect() as conn:
            cursor = await conn.execute(
                "SELECT * FROM promo_codes WHERE code = ?", (code.strip().upper(),)
            )
            row = await cursor.fetchone()
            return PromoCode.from_row(row) if row else None

    async def get_all_promo_codes(self) -> List[PromoCode]:
        """Barcha promo kodlar ro'yxatini qaytaradi."""
        async with self._connect() as conn:
            cursor = await conn.execute("SELECT * FROM promo_codes ORDER BY id DESC")
            rows = await cursor.fetchall()
            return [PromoCode.from_row(row) for row in rows]

    async def update_promo_code(
        self,
        promo_id: int,
        discount_percent: Optional[int] = None,
        discount_amount: Optional[float] = None,
        free_uc_amount: Optional[int] = None,
        max_uses: Optional[int] = None,
        expires_at: Optional[str] = None,
    ) -> None:
        """Mavjud promo kodni tahrirlaydi (faqat berilgan maydonlarni)."""
        promo = await self.get_promo_code(promo_id)
        if not promo:
            return

        async with self._connect() as conn:
            await conn.execute(
                """
                UPDATE promo_codes
                SET discount_percent = ?, discount_amount = ?, free_uc_amount = ?,
                    max_uses = ?, expires_at = ?
                WHERE id = ?
                """,
                (
                    discount_percent if discount_percent is not None else promo.discount_percent,
                    discount_amount if discount_amount is not None else promo.discount_amount,
                    free_uc_amount if free_uc_amount is not None else promo.free_uc_amount,
                    max_uses if max_uses is not None else promo.max_uses,
                    expires_at if expires_at is not None else promo.expires_at,
                    promo_id,
                ),
            )
            await conn.commit()

    async def set_promo_code_active(self, promo_id: int, is_active: bool) -> None:
        """Promo kodni yoqadi yoki o'chiradi."""
        async with self._connect() as conn:
            await conn.execute(
                "UPDATE promo_codes SET is_active = ? WHERE id = ?",
                (1 if is_active else 0, promo_id),
            )
            await conn.commit()

    async def delete_promo_code(self, promo_id: int) -> None:
        """Promo kodni database'dan butunlay o'chiradi."""
        async with self._connect() as conn:
            await conn.execute("DELETE FROM promo_codes WHERE id = ?", (promo_id,))
            await conn.commit()

    async def has_user_used_promo(self, promo_id: int, telegram_id: int) -> bool:
        """Foydalanuvchi shu promo kodni ilgari ishlatganligini tekshiradi."""
        async with self._connect() as conn:
            cursor = await conn.execute(
                "SELECT id FROM promo_code_usages WHERE promo_id = ? AND telegram_id = ?",
                (promo_id, telegram_id),
            )
            row = await cursor.fetchone()
            return row is not None

    async def record_promo_usage(
        self, promo_id: int, telegram_id: int, order_id: Optional[int] = None
    ) -> None:
        """Promo kod ishlatilganini qayd etadi va ishlatilish sonini oshiradi."""
        async with self._connect() as conn:
            await conn.execute(
                """
                INSERT INTO promo_code_usages (promo_id, telegram_id, order_id, used_at)
                VALUES (?, ?, ?, ?)
                """,
                (promo_id, telegram_id, order_id, current_timestamp()),
            )
            await conn.execute(
                "UPDATE promo_codes SET used_count = used_count + 1 WHERE id = ?",
                (promo_id,),
            )
            await conn.commit()

    # ==========================================================
    # YANGI: REFERRAL TIZIMI
    # ==========================================================

    async def add_referral(
        self, referrer_telegram_id: int, referred_telegram_id: int, bonus_amount: float = 0.0
    ) -> Optional[int]:
        """
        Yangi referral bog'lanishini qo'shadi (bitta foydalanuvchi faqat
        bir marta taklif qilingan hisoblanadi).

        Returns:
            Yangi yozuv ID si, yoki agar allaqachon mavjud bo'lsa None.
        """
        async with self._connect() as conn:
            existing = await conn.execute(
                "SELECT id FROM referrals WHERE referred_telegram_id = ?",
                (referred_telegram_id,),
            )
            if await existing.fetchone():
                return None

            cursor = await conn.execute(
                """
                INSERT INTO referrals (referrer_telegram_id, referred_telegram_id, bonus_amount, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (referrer_telegram_id, referred_telegram_id, bonus_amount, current_timestamp()),
            )
            await conn.commit()
            return cursor.lastrowid

    async def get_referral_by_referred(self, referred_telegram_id: int) -> Optional[Referral]:
        """Foydalanuvchi kim tomonidan taklif qilinganini qaytaradi."""
        async with self._connect() as conn:
            cursor = await conn.execute(
                "SELECT * FROM referrals WHERE referred_telegram_id = ?",
                (referred_telegram_id,),
            )
            row = await cursor.fetchone()
            return Referral.from_row(row) if row else None

    async def count_referrals_by_user(self, referrer_telegram_id: int) -> int:
        """Foydalanuvchi jami nechta odam taklif qilganini hisoblaydi."""
        async with self._connect() as conn:
            cursor = await conn.execute(
                "SELECT COUNT(*) as cnt FROM referrals WHERE referrer_telegram_id = ?",
                (referrer_telegram_id,),
            )
            row = await cursor.fetchone()
            return row["cnt"] if row else 0

    async def get_referrals_by_user(self, referrer_telegram_id: int) -> List[Referral]:
        """Foydalanuvchi taklif qilgan barcha referrallar ro'yxatini qaytaradi."""
        async with self._connect() as conn:
            cursor = await conn.execute(
                "SELECT * FROM referrals WHERE referrer_telegram_id = ? ORDER BY id DESC",
                (referrer_telegram_id,),
            )
            rows = await cursor.fetchall()
            return [Referral.from_row(row) for row in rows]

    # ==========================================================
    # YANGI: BANNER
    # ==========================================================

    async def set_banner(self, text: str, image_file_id: Optional[str] = None) -> int:
        """
        Yangi bannerni faol qilib o'rnatadi. Avvalgi barcha bannerlar
        avtomatik nofaol holatga o'tkaziladi (bir vaqtda faqat bitta
        faol banner bo'lishi uchun).
        """
        async with self._connect() as conn:
            await conn.execute("UPDATE banners SET is_active = 0")
            cursor = await conn.execute(
                """
                INSERT INTO banners (text, image_file_id, is_active, created_at)
                VALUES (?, ?, 1, ?)
                """,
                (text, image_file_id, current_timestamp()),
            )
            await conn.commit()
            return cursor.lastrowid

    async def get_active_banner(self) -> Optional[Banner]:
        """Hozirda faol bo'lgan bannerni qaytaradi (agar mavjud bo'lsa)."""
        async with self._connect() as conn:
            cursor = await conn.execute(
                "SELECT * FROM banners WHERE is_active = 1 ORDER BY id DESC LIMIT 1"
            )
            row = await cursor.fetchone()
            return Banner.from_row(row) if row else None

    async def deactivate_banner(self) -> None:
        """Faol bannerni o'chiradi (bot boshida ko'rinmaydigan qiladi)."""
        async with self._connect() as conn:
            await conn.execute("UPDATE banners SET is_active = 0")
            await conn.commit()

    # ==========================================================
    # YANGI: YANGILIKLAR
    # ==========================================================

    async def add_news(self, title: str, text: str, image_file_id: Optional[str] = None) -> int:
        """Yangi yangilik/aksiya postini qo'shadi."""
        async with self._connect() as conn:
            cursor = await conn.execute(
                """
                INSERT INTO news (title, text, image_file_id, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (title, text, image_file_id, current_timestamp()),
            )
            await conn.commit()
            return cursor.lastrowid

    async def get_news(self, news_id: int) -> Optional[NewsPost]:
        """ID orqali bitta yangilikni qaytaradi."""
        async with self._connect() as conn:
            cursor = await conn.execute("SELECT * FROM news WHERE id = ?", (news_id,))
            row = await cursor.fetchone()
            return NewsPost.from_row(row) if row else None

    async def get_all_news(self) -> List[NewsPost]:
        """Barcha yangiliklar ro'yxatini (yangi birinchi) qaytaradi."""
        async with self._connect() as conn:
            cursor = await conn.execute("SELECT * FROM news ORDER BY id DESC")
            rows = await cursor.fetchall()
            return [NewsPost.from_row(row) for row in rows]

    async def update_news(
        self, news_id: int, title: Optional[str] = None, text: Optional[str] = None
    ) -> None:
        """Mavjud yangilikni tahrirlaydi."""
        news = await self.get_news(news_id)
        if not news:
            return

        async with self._connect() as conn:
            await conn.execute(
                "UPDATE news SET title = ?, text = ? WHERE id = ?",
                (
                    title if title is not None else news.title,
                    text if text is not None else news.text,
                    news_id,
                ),
            )
            await conn.commit()

    async def delete_news(self, news_id: int) -> None:
        """Yangilikni database'dan butunlay o'chiradi."""
        async with self._connect() as conn:
            await conn.execute("DELETE FROM news WHERE id = ?", (news_id,))
            await conn.commit()

    # ==========================================================
    # YANGI: TO'LOV USULLARI
    # ==========================================================

    async def add_payment_method(self, name: str, card_number: str, card_owner: str) -> int:
        """Yangi to'lov usulini (karta) qo'shadi."""
        async with self._connect() as conn:
            cursor = await conn.execute(
                """
                INSERT INTO payment_methods (name, card_number, card_owner, is_active, created_at)
                VALUES (?, ?, ?, 1, ?)
                """,
                (name, card_number, card_owner, current_timestamp()),
            )
            await conn.commit()
            return cursor.lastrowid

    async def get_payment_method(self, payment_method_id: int) -> Optional[PaymentMethod]:
        """ID orqali bitta to'lov usulini qaytaradi."""
        async with self._connect() as conn:
            cursor = await conn.execute(
                "SELECT * FROM payment_methods WHERE id = ?", (payment_method_id,)
            )
            row = await cursor.fetchone()
            return PaymentMethod.from_row(row) if row else None

    async def get_all_payment_methods(self, only_active: bool = False) -> List[PaymentMethod]:
        """Barcha to'lov usullari ro'yxatini qaytaradi."""
        async with self._connect() as conn:
            query = "SELECT * FROM payment_methods"
            if only_active:
                query += " WHERE is_active = 1"
            query += " ORDER BY id ASC"
            cursor = await conn.execute(query)
            rows = await cursor.fetchall()
            return [PaymentMethod.from_row(row) for row in rows]

    async def update_payment_method(
        self,
        payment_method_id: int,
        name: Optional[str] = None,
        card_number: Optional[str] = None,
        card_owner: Optional[str] = None,
    ) -> None:
        """Mavjud to'lov usulini tahrirlaydi."""
        method = await self.get_payment_method(payment_method_id)
        if not method:
            return

        async with self._connect() as conn:
            await conn.execute(
                """
                UPDATE payment_methods
                SET name = ?, card_number = ?, card_owner = ?
                WHERE id = ?
                """,
                (
                    name if name is not None else method.name,
                    card_number if card_number is not None else method.card_number,
                    card_owner if card_owner is not None else method.card_owner,
                    payment_method_id,
                ),
            )
            await conn.commit()

    async def set_payment_method_active(self, payment_method_id: int, is_active: bool) -> None:
        """To'lov usulini yoqadi yoki o'chiradi."""
        async with self._connect() as conn:
            await conn.execute(
                "UPDATE payment_methods SET is_active = ? WHERE id = ?",
                (1 if is_active else 0, payment_method_id),
            )
            await conn.commit()

    async def delete_payment_method(self, payment_method_id: int) -> None:
        """To'lov usulini database'dan butunlay o'chiradi."""
        async with self._connect() as conn:
            await conn.execute(
                "DELETE FROM payment_methods WHERE id = ?", (payment_method_id,)
            )
            await conn.commit()

    # ==========================================================
    # YANGI: ADMIN LOG
    # ==========================================================

    async def add_admin_log(self, admin_telegram_id: int, action: str, details: Optional[str] = None) -> None:
        """Admin tomonidan qilingan amalni log sifatida saqlaydi."""
        async with self._connect() as conn:
            await conn.execute(
                """
                INSERT INTO admin_logs (admin_telegram_id, action, details, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (admin_telegram_id, action, details, current_timestamp()),
            )
            await conn.commit()

    async def get_recent_admin_logs(self, limit: int = 50) -> List[AdminLog]:
        """Eng so'nggi admin amallarini (log) qaytaradi."""
        async with self._connect() as conn:
            cursor = await conn.execute(
                "SELECT * FROM admin_logs ORDER BY id DESC LIMIT ?", (limit,)
            )
            rows = await cursor.fetchall()
            return [AdminLog.from_row(row) for row in rows]

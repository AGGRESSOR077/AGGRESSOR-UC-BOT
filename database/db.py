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
    Order,
    Package,
    Settings,
    User,
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

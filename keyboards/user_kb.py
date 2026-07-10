"""
AGGRESSOR UC BOT - Mijoz uchun klaviaturalar moduli.

Bu modulda mijozlarga ko'rsatiladigan barcha Inline Keyboard'lar
yaratiladi.
"""

from typing import List

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.models import Package


def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Asosiy menyu klaviaturasi (start bosilganda chiqadi)."""
    builder = InlineKeyboardBuilder()
    builder.button(text="💎 UC sotib olish", callback_data="buy_uc")
    builder.button(text="💰 Narxlarni ko'rish", callback_data="show_prices")
    builder.button(text="☎ Contact Us", callback_data="contact_us")
    builder.adjust(1)
    return builder.as_markup()


def back_to_menu_keyboard() -> InlineKeyboardMarkup:
    """Asosiy menyuga qaytish tugmasi."""
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅ Asosiy menyu", callback_data="back_to_main_menu")
    builder.adjust(1)
    return builder.as_markup()


def packages_keyboard(packages: List[Package]) -> InlineKeyboardMarkup:
    """
    Mavjud paketlar ro'yxatini Inline Keyboard sifatida chiqaradi.

    Har bir tugma bosilganda `select_package:{package_id}` callback yuboriladi.
    """
    builder = InlineKeyboardBuilder()
    for package in packages:
        builder.button(
            text=f"{package.display_name()} — {package.display_price()}",
            callback_data=f"select_package:{package.id}",
        )
    builder.button(text="⬅ Asosiy menyu", callback_data="back_to_main_menu")
    builder.adjust(1)
    return builder.as_markup()


def cancel_order_keyboard() -> InlineKeyboardMarkup:
    """Buyurtma jarayonida bekor qilish tugmasi."""
    builder = InlineKeyboardBuilder()
    builder.button(text="🚫 Bekor qilish", callback_data="cancel_order")
    builder.adjust(1)
    return builder.as_markup()


def order_confirmation_keyboard(package_id: int) -> InlineKeyboardMarkup:
    """Paket tanlanganidan keyin tasdiqlash/bekor qilish tugmalari."""
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Tasdiqlash", callback_data=f"confirm_package:{package_id}")
    builder.button(text="🚫 Bekor qilish", callback_data="cancel_order")
    builder.adjust(2)
    return builder.as_markup()

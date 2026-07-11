# 📁 JOYLASHUV: aggressor_uc_bot/keyboards/user_kb.py
# ⚠ MAVJUD FAYL — bu faylni to'liq shu nom bilan almashtiring
# (mavjud funksiyalar o'zgarishsiz qoldi, yangi funksiyalar qo'shildi).
"""
AGGRESSOR UC BOT - Mijoz uchun klaviaturalar moduli.

Bu modulda mijozlarga ko'rsatiladigan barcha Inline Keyboard'lar
yaratiladi.
"""

from typing import List

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.models import Order, Package, PaymentMethod


def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Asosiy menyu klaviaturasi (start bosilganda chiqadi)."""
    builder = InlineKeyboardBuilder()
    builder.button(text="💎 UC sotib olish", callback_data="buy_uc")
    builder.button(text="💰 Narxlarni ko'rish", callback_data="show_prices")
    builder.button(text="☎ Contact Us", callback_data="contact_us")
    # ---- YANGI: qo'shimcha bo'limlar (mavjud tugmalar tartibi o'zgarmadi) ----
    builder.button(text="📦 Mening buyurtmalarim", callback_data="my_orders")
    builder.button(text="🤝 Referral", callback_data="referral_menu")
    builder.button(text="🧮 UC Calculator", callback_data="uc_calculator")
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


# ==========================================================
# YANGI: BUYURTMALAR TARIXI
# ==========================================================


def my_orders_keyboard(orders: List[Order]) -> InlineKeyboardMarkup:
    """
    Foydalanuvchining barcha buyurtmalari ro'yxatini ko'rsatuvchi klaviatura.

    Har bir tugma bosilganda `view_my_order:{order_id}` callback yuboriladi.
    """
    builder = InlineKeyboardBuilder()
    for order in orders:
        builder.button(
            text=f"{order.order_number} — {order.status_display()}",
            callback_data=f"view_my_order:{order.id}",
        )
    builder.button(text="⬅ Asosiy menyu", callback_data="back_to_main_menu")
    builder.adjust(1)
    return builder.as_markup()


def order_detail_user_keyboard(order_id: int, show_rating: bool = False) -> InlineKeyboardMarkup:
    """
    Bitta buyurtma tafsilotlari ostidagi klaviatura.

    Args:
        show_rating: Agar True bo'lsa, reyting berish tugmasi ham chiqadi
            (buyurtma "completed" va hali baholanmagan bo'lsa).
    """
    builder = InlineKeyboardBuilder()
    if show_rating:
        builder.button(text="⭐ Baho berish", callback_data=f"rate_prompt:{order_id}")
    builder.button(text="⬅ Buyurtmalarim", callback_data="my_orders")
    builder.adjust(1)
    return builder.as_markup()


# ==========================================================
# YANGI: REYTING (1-5 ⭐)
# ==========================================================


def rating_keyboard(order_id: int) -> InlineKeyboardMarkup:
    """Buyurtmaga 1 dan 5 gacha yulduzcha bilan baho berish klaviaturasi."""
    builder = InlineKeyboardBuilder()
    for stars in range(1, 6):
        builder.button(
            text="⭐" * stars,
            callback_data=f"rate_order:{order_id}:{stars}",
        )
    builder.adjust(1)
    return builder.as_markup()


# ==========================================================
# YANGI: PROMO KOD (buyurtma jarayonida)
# ==========================================================


def promo_entry_keyboard() -> InlineKeyboardMarkup:
    """Buyurtma jarayonida promo kod kiritish bosqichidagi klaviatura."""
    builder = InlineKeyboardBuilder()
    builder.button(text="⏭ O'tkazib yuborish", callback_data="skip_promo")
    builder.button(text="🚫 Bekor qilish", callback_data="cancel_order")
    builder.adjust(1)
    return builder.as_markup()


# ==========================================================
# YANGI: TO'LOV USULINI TANLASH
# ==========================================================


def payment_method_choice_keyboard(methods: List[PaymentMethod]) -> InlineKeyboardMarkup:
    """
    Bir nechta to'lov usuli mavjud bo'lganda, mijoz tanlashi uchun klaviatura.

    Har bir tugma bosilganda `choose_payment:{method_id}` callback yuboriladi.
    """
    builder = InlineKeyboardBuilder()
    for method in methods:
        builder.button(text=f"💳 {method.name}", callback_data=f"choose_payment:{method.id}")
    builder.button(text="🚫 Bekor qilish", callback_data="cancel_order")
    builder.adjust(1)
    return builder.as_markup()


# ==========================================================
# YANGI: REFERRAL MENYUSI
# ==========================================================


def referral_menu_keyboard() -> InlineKeyboardMarkup:
    """Referral bo'limi ostidagi klaviatura."""
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅ Asosiy menyu", callback_data="back_to_main_menu")
    builder.adjust(1)
    return builder.as_markup()


# ==========================================================
# YANGI: UC CALCULATOR
# ==========================================================


def uc_calculator_keyboard() -> InlineKeyboardMarkup:
    """UC Calculator bo'limi ostidagi klaviatura."""
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅ Asosiy menyu", callback_data="back_to_main_menu")
    builder.adjust(1)
    return builder.as_markup()

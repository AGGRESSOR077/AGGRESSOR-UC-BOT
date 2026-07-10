"""
AGGRESSOR UC BOT - Admin uchun klaviaturalar moduli.

Bu modulda adminlarga ko'rsatiladigan barcha Inline Keyboard'lar
yaratiladi.
"""

from typing import List

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.models import Package


def admin_panel_keyboard() -> InlineKeyboardMarkup:
    """Admin panel asosiy menyusi."""
    builder = InlineKeyboardBuilder()
    builder.button(text="📦 Buyurtmalar", callback_data="admin_orders")
    builder.button(text="➕ Paket qo'shish", callback_data="admin_add_package")
    builder.button(text="✏ Paketni tahrirlash", callback_data="admin_edit_package")
    builder.button(text="❌ Paketni o'chirish", callback_data="admin_delete_package")
    builder.button(text="💰 Narxlarni o'zgartirish", callback_data="admin_change_prices")
    builder.button(text="📊 Statistika", callback_data="admin_statistics")
    builder.button(text="📢 Broadcast", callback_data="admin_broadcast")
    builder.button(text="⚙ Sozlamalar", callback_data="admin_settings")
    builder.adjust(2, 2, 2, 1, 1)
    return builder.as_markup()


def back_to_admin_panel_keyboard() -> InlineKeyboardMarkup:
    """Admin panelga qaytish tugmasi."""
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅ Admin panel", callback_data="back_to_admin_panel")
    builder.adjust(1)
    return builder.as_markup()


def orders_filter_keyboard() -> InlineKeyboardMarkup:
    """Buyurtmalarni holat bo'yicha filtrlash klaviaturasi."""
    builder = InlineKeyboardBuilder()
    builder.button(text="⏳ Kutilmoqda", callback_data="orders_status:pending")
    builder.button(text="✅ Tasdiqlangan", callback_data="orders_status:confirmed")
    builder.button(text="🎮 Bajarilgan", callback_data="orders_status:completed")
    builder.button(text="❌ Bekor qilingan", callback_data="orders_status:cancelled")
    builder.button(text="⬅ Admin panel", callback_data="back_to_admin_panel")
    builder.adjust(2, 2, 1)
    return builder.as_markup()


def order_action_keyboard(order_id: int) -> InlineKeyboardMarkup:
    """
    Yangi buyurtma uchun admin ko'radigan tugmalar:
    ✅ To'lov tasdiqlandi / ❌ Bekor qilish
    """
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ To'lov tasdiqlandi", callback_data=f"confirm_order:{order_id}")
    builder.button(text="❌ Bekor qilish", callback_data=f"cancel_order_admin:{order_id}")
    builder.adjust(2)
    return builder.as_markup()


def order_send_uc_keyboard(order_id: int) -> InlineKeyboardMarkup:
    """To'lov tasdiqlangandan keyin chiqadigan '🎮 UC yuborildi' tugmasi."""
    builder = InlineKeyboardBuilder()
    builder.button(text="🎮 UC yuborildi", callback_data=f"uc_sent:{order_id}")
    builder.adjust(1)
    return builder.as_markup()


def packages_list_keyboard(packages: List[Package], action: str) -> InlineKeyboardMarkup:
    """
    Paketlar ro'yxatini tanlash uchun klaviatura.

    action: "edit" yoki "delete" — callback_data prefiksini belgilaydi.
    """
    builder = InlineKeyboardBuilder()
    for package in packages:
        builder.button(
            text=f"{package.display_name()} — {package.display_price()}",
            callback_data=f"{action}_pkg:{package.id}",
        )
    builder.button(text="⬅ Admin panel", callback_data="back_to_admin_panel")
    builder.adjust(1)
    return builder.as_markup()


def package_edit_field_keyboard(package_id: int) -> InlineKeyboardMarkup:
    """Paketni tahrirlashda qaysi maydonni o'zgartirish tanlovi."""
    builder = InlineKeyboardBuilder()
    builder.button(text="📝 Nomi", callback_data=f"edit_field:name:{package_id}")
    builder.button(text="🔢 UC miqdori", callback_data=f"edit_field:uc_amount:{package_id}")
    builder.button(text="💰 Narxi", callback_data=f"edit_field:price:{package_id}")
    builder.button(text="⬅ Admin panel", callback_data="back_to_admin_panel")
    builder.adjust(1)
    return builder.as_markup()


def confirm_delete_keyboard(package_id: int) -> InlineKeyboardMarkup:
    """Paketni o'chirishni tasdiqlash/bekor qilish klaviaturasi."""
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Ha, o'chirish", callback_data=f"confirm_delete_pkg:{package_id}")
    builder.button(text="🚫 Bekor qilish", callback_data="back_to_admin_panel")
    builder.adjust(2)
    return builder.as_markup()


def settings_menu_keyboard() -> InlineKeyboardMarkup:
    """Sozlamalar menyusi klaviaturasi."""
    builder = InlineKeyboardBuilder()
    builder.button(text="💳 Karta raqamini o'zgartirish", callback_data="settings_change_card_number")
    builder.button(text="👤 Karta egasini o'zgartirish", callback_data="settings_change_card_owner")
    builder.button(text="⬅ Admin panel", callback_data="back_to_admin_panel")
    builder.adjust(1)
    return builder.as_markup()


def broadcast_confirm_keyboard() -> InlineKeyboardMarkup:
    """Broadcast xabarini yuborishni tasdiqlash klaviaturasi."""
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Yuborish", callback_data="broadcast_confirm")
    builder.button(text="🚫 Bekor qilish", callback_data="broadcast_cancel")
    builder.adjust(2)
    return builder.as_markup()


def cancel_action_keyboard() -> InlineKeyboardMarkup:
    """Har qanday admin FSM jarayonini bekor qilish tugmasi."""
    builder = InlineKeyboardBuilder()
    builder.button(text="🚫 Bekor qilish", callback_data="admin_cancel_action")
    builder.adjust(1)
    return builder.as_markup()

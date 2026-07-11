# 📁 JOYLASHUV: aggressor_uc_bot/keyboards/admin_kb.py
# ⚠ MAVJUD FAYL — bu faylni to'liq shu nom bilan almashtiring
# (mavjud funksiyalar o'zgarishsiz qoldi, yangi funksiyalar qo'shildi).
"""
AGGRESSOR UC BOT - Admin uchun klaviaturalar moduli.

Bu modulda adminlarga ko'rsatiladigan barcha Inline Keyboard'lar
yaratiladi.
"""

from typing import List, Optional

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.models import NewsPost, PaymentMethod, PromoCode, User, Package


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
    # ---- YANGI: qo'shimcha bo'limlar (mavjud tugmalar tartibi o'zgarmadi) ----
    builder.button(text="👥 Foydalanuvchilar", callback_data="admin_users")
    builder.button(text="🎁 Promo kodlar", callback_data="admin_promo")
    builder.button(text="🤝 Referral sozlamalari", callback_data="admin_referral_settings")
    builder.button(text="🖼 Banner", callback_data="admin_banner")
    builder.button(text="📰 Yangiliklar", callback_data="admin_news")
    builder.button(text="💳 To'lov usullari", callback_data="admin_payment_methods")
    builder.button(text="📋 Admin log", callback_data="admin_logs")
    builder.adjust(2, 2, 2, 1, 1, 2, 2, 2, 1)
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


def order_action_keyboard(order_id: int, telegram_id: Optional[int] = None) -> InlineKeyboardMarkup:
    """
    Yangi buyurtma uchun admin ko'radigan tugmalar:
    ✅ To'lov tasdiqlandi / ❌ Bekor qilish

    Args:
        telegram_id: Agar berilsa, buyurtma egasini bevosita shu oynadan
            ban qilish uchun qo'shimcha "🚫 Ban qilish" tugmasi chiqadi
            (YANGI: Ban tizimi buyurtma oynasidan).
    """
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ To'lov tasdiqlandi", callback_data=f"confirm_order:{order_id}")
    builder.button(text="❌ Bekor qilish", callback_data=f"cancel_order_admin:{order_id}")
    if telegram_id is not None:
        builder.button(text="🚫 Ban qilish", callback_data=f"ban_user_start:{telegram_id}")
        builder.adjust(2, 1)
    else:
        builder.adjust(2)
    return builder.as_markup()


def order_send_uc_keyboard(order_id: int, telegram_id: Optional[int] = None) -> InlineKeyboardMarkup:
    """
    To'lov tasdiqlangandan keyin chiqadigan '🎮 UC yuborildi' tugmasi.

    Args:
        telegram_id: Agar berilsa, qo'shimcha "🚫 Ban qilish" tugmasi chiqadi.
    """
    builder = InlineKeyboardBuilder()
    builder.button(text="🎮 UC yuborildi", callback_data=f"uc_sent:{order_id}")
    if telegram_id is not None:
        builder.button(text="🚫 Ban qilish", callback_data=f"ban_user_start:{telegram_id}")
        builder.adjust(1, 1)
    else:
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


# ==========================================================
# YANGI: FOYDALANUVCHILAR (pagination)
# ==========================================================


def users_pagination_keyboard(users: List[User], page: int, total_pages: int) -> InlineKeyboardMarkup:
    """
    Foydalanuvchilar ro'yxatini pagination bilan ko'rsatuvchi klaviatura.

    Har bir foydalanuvchi alohida tugma, pastda ⬅️/➡️ navigatsiya.
    """
    builder = InlineKeyboardBuilder()
    for user in users:
        name = user.full_name or "Noma'lum"
        username_part = f"@{user.username}" if user.username else "username yo'q"
        builder.button(
            text=f"{name} | {username_part}",
            callback_data=f"view_user:{user.telegram_id}",
        )
    builder.adjust(1)

    nav_builder = InlineKeyboardBuilder()
    if page > 1:
        nav_builder.button(text="⬅️ Oldingi", callback_data=f"users_page:{page - 1}")
    nav_builder.button(text=f"{page}/{total_pages}", callback_data="noop")
    if page < total_pages:
        nav_builder.button(text="Keyingi ➡️", callback_data=f"users_page:{page + 1}")
    nav_builder.adjust(3)

    builder.attach(nav_builder)

    back_builder = InlineKeyboardBuilder()
    back_builder.button(text="⬅ Admin panel", callback_data="back_to_admin_panel")
    back_builder.adjust(1)
    builder.attach(back_builder)

    return builder.as_markup()


def user_profile_action_keyboard(telegram_id: int, is_banned: bool) -> InlineKeyboardMarkup:
    """
    Bitta foydalanuvchi profili ostidagi amallar klaviaturasi:
    Buyurtmalar / Xabar yuborish / Ban(dan chiqarish) / Ortga.
    """
    builder = InlineKeyboardBuilder()
    builder.button(text="📦 Buyurtmalar", callback_data=f"view_user_orders:{telegram_id}")
    builder.button(text="📨 Xabar yuborish", callback_data=f"message_user:{telegram_id}")
    if is_banned:
        builder.button(text="🔓 Bandan chiqarish", callback_data=f"unban_user:{telegram_id}")
    else:
        builder.button(text="🚫 Ban qilish", callback_data=f"ban_user_start:{telegram_id}")
    builder.button(text="⬅ Ortga", callback_data="admin_users")
    builder.adjust(1, 1, 1, 1)
    return builder.as_markup()


# ==========================================================
# YANGI: PROMO KOD BOSHQARUVI
# ==========================================================


def promo_type_choice_keyboard() -> InlineKeyboardMarkup:
    """Promo kod turini tanlash klaviaturasi."""
    builder = InlineKeyboardBuilder()
    builder.button(text="🔢 Foizli chegirma", callback_data="promo_type:percent")
    builder.button(text="💰 Belgilangan summa", callback_data="promo_type:fixed")
    builder.button(text="🎮 Bepul UC", callback_data="promo_type:free_uc")
    builder.button(text="🚫 Bekor qilish", callback_data="admin_cancel_action")
    builder.adjust(1)
    return builder.as_markup()


def promo_list_keyboard(promo_codes: List[PromoCode]) -> InlineKeyboardMarkup:
    """Promo kodlar ro'yxatini ko'rsatuvchi klaviatura."""
    builder = InlineKeyboardBuilder()
    for promo in promo_codes:
        status_icon = "✅" if promo.is_active else "🚫"
        builder.button(
            text=f"{status_icon} {promo.code}",
            callback_data=f"view_promo:{promo.id}",
        )
    builder.button(text="➕ Yangi promo kod", callback_data="admin_add_promo")
    builder.button(text="⬅ Admin panel", callback_data="back_to_admin_panel")
    builder.adjust(1)
    return builder.as_markup()


def promo_detail_keyboard(promo_id: int, is_active: bool) -> InlineKeyboardMarkup:
    """Bitta promo kod tafsilotlari ostidagi amallar klaviaturasi."""
    builder = InlineKeyboardBuilder()
    if is_active:
        builder.button(text="🚫 O'chirish (nofaol)", callback_data=f"toggle_promo:{promo_id}:off")
    else:
        builder.button(text="✅ Yoqish", callback_data=f"toggle_promo:{promo_id}:on")
    builder.button(text="🗑 Butunlay o'chirish", callback_data=f"delete_promo:{promo_id}")
    builder.button(text="⬅ Promo kodlar", callback_data="admin_promo")
    builder.adjust(1)
    return builder.as_markup()


def confirm_delete_promo_keyboard(promo_id: int) -> InlineKeyboardMarkup:
    """Promo kodni o'chirishni tasdiqlash klaviaturasi."""
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Ha, o'chirish", callback_data=f"confirm_delete_promo:{promo_id}")
    builder.button(text="🚫 Bekor qilish", callback_data=f"view_promo:{promo_id}")
    builder.adjust(2)
    return builder.as_markup()


# ==========================================================
# YANGI: REFERRAL SOZLAMALARI
# ==========================================================


def referral_settings_keyboard(is_enabled: bool) -> InlineKeyboardMarkup:
    """Referral tizimi sozlamalari klaviaturasi."""
    builder = InlineKeyboardBuilder()
    if is_enabled:
        builder.button(text="🚫 O'chirish", callback_data="referral_toggle:off")
    else:
        builder.button(text="✅ Yoqish", callback_data="referral_toggle:on")
    builder.button(text="💰 Minimal summa", callback_data="referral_set_min_order")
    builder.button(text="🎁 Bonus turi", callback_data="referral_set_bonus_type")
    builder.button(text="🎁 Bonus qiymati", callback_data="referral_set_bonus_value")
    builder.button(text="🎯 Chegara soni", callback_data="referral_set_threshold_count")
    builder.button(text="🎯 Chegara chegirmasi", callback_data="referral_set_threshold_percent")
    builder.button(text="⬅ Admin panel", callback_data="back_to_admin_panel")
    builder.adjust(1, 2, 2, 2, 1)
    return builder.as_markup()


def referral_bonus_type_keyboard() -> InlineKeyboardMarkup:
    """Referral bonusi turini tanlash klaviaturasi."""
    builder = InlineKeyboardBuilder()
    builder.button(text="💵 Pul", callback_data="referral_bonus_type:money")
    builder.button(text="🎫 Chegirma", callback_data="referral_bonus_type:discount")
    builder.button(text="🎮 UC narxiga chegirma", callback_data="referral_bonus_type:uc_discount")
    builder.button(text="⬅ Admin panel", callback_data="back_to_admin_panel")
    builder.adjust(1)
    return builder.as_markup()


# ==========================================================
# YANGI: BANNER
# ==========================================================


def banner_menu_keyboard(has_active_banner: bool) -> InlineKeyboardMarkup:
    """Banner boshqaruvi menyusi klaviaturasi."""
    builder = InlineKeyboardBuilder()
    builder.button(text="🖼 Banner o'rnatish", callback_data="banner_set")
    if has_active_banner:
        builder.button(text="🗑 Bannerni olib tashlash", callback_data="banner_remove")
    builder.button(text="⬅ Admin panel", callback_data="back_to_admin_panel")
    builder.adjust(1)
    return builder.as_markup()


def skip_image_keyboard() -> InlineKeyboardMarkup:
    """Rasm yuborish ixtiyoriy bo'lgan bosqichlarda o'tkazib yuborish tugmasi."""
    builder = InlineKeyboardBuilder()
    builder.button(text="⏭ O'tkazib yuborish", callback_data="skip_image")
    builder.button(text="🚫 Bekor qilish", callback_data="admin_cancel_action")
    builder.adjust(1)
    return builder.as_markup()


# ==========================================================
# YANGI: YANGILIKLAR
# ==========================================================


def news_list_keyboard(news_list: List[NewsPost]) -> InlineKeyboardMarkup:
    """Yangiliklar ro'yxatini ko'rsatuvchi klaviatura."""
    builder = InlineKeyboardBuilder()
    for news in news_list:
        builder.button(text=f"📰 {news.title}", callback_data=f"view_news:{news.id}")
    builder.button(text="➕ Yangi yangilik", callback_data="admin_add_news")
    builder.button(text="⬅ Admin panel", callback_data="back_to_admin_panel")
    builder.adjust(1)
    return builder.as_markup()


def news_detail_keyboard(news_id: int) -> InlineKeyboardMarkup:
    """Bitta yangilik tafsilotlari ostidagi amallar klaviaturasi."""
    builder = InlineKeyboardBuilder()
    builder.button(text="📢 Foydalanuvchilarga yuborish", callback_data=f"broadcast_news:{news_id}")
    builder.button(text="🗑 O'chirish", callback_data=f"delete_news:{news_id}")
    builder.button(text="⬅ Yangiliklar", callback_data="admin_news")
    builder.adjust(1)
    return builder.as_markup()


def confirm_delete_news_keyboard(news_id: int) -> InlineKeyboardMarkup:
    """Yangilikni o'chirishni tasdiqlash klaviaturasi."""
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Ha, o'chirish", callback_data=f"confirm_delete_news:{news_id}")
    builder.button(text="🚫 Bekor qilish", callback_data=f"view_news:{news_id}")
    builder.adjust(2)
    return builder.as_markup()


# ==========================================================
# YANGI: TO'LOV USULLARI
# ==========================================================


def payment_methods_list_keyboard(methods: List[PaymentMethod]) -> InlineKeyboardMarkup:
    """To'lov usullari ro'yxatini ko'rsatuvchi klaviatura."""
    builder = InlineKeyboardBuilder()
    for method in methods:
        status_icon = "✅" if method.is_active else "🚫"
        builder.button(
            text=f"{status_icon} {method.name}",
            callback_data=f"view_payment_method:{method.id}",
        )
    builder.button(text="➕ Yangi to'lov usuli", callback_data="admin_add_payment_method")
    builder.button(text="⬅ Admin panel", callback_data="back_to_admin_panel")
    builder.adjust(1)
    return builder.as_markup()


def payment_method_detail_keyboard(method_id: int, is_active: bool) -> InlineKeyboardMarkup:
    """Bitta to'lov usuli tafsilotlari ostidagi amallar klaviaturasi."""
    builder = InlineKeyboardBuilder()
    if is_active:
        builder.button(text="🚫 O'chirish (nofaol)", callback_data=f"toggle_payment_method:{method_id}:off")
    else:
        builder.button(text="✅ Yoqish", callback_data=f"toggle_payment_method:{method_id}:on")
    builder.button(text="🗑 Butunlay o'chirish", callback_data=f"delete_payment_method:{method_id}")
    builder.button(text="⬅ To'lov usullari", callback_data="admin_payment_methods")
    builder.adjust(1)
    return builder.as_markup()


# ==========================================================
# YANGI: ADMIN LOG
# ==========================================================


def admin_logs_keyboard() -> InlineKeyboardMarkup:
    """Admin log bo'limi ostidagi klaviatura."""
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅ Admin panel", callback_data="back_to_admin_panel")
    builder.adjust(1)
    return builder.as_markup()


# ==========================================================
# YANGI: BAN TIZIMI
# ==========================================================


def ban_reason_cancel_keyboard() -> InlineKeyboardMarkup:
    """Ban sababi kiritish bosqichida bekor qilish klaviaturasi."""
    builder = InlineKeyboardBuilder()
    builder.button(text="🚫 Bekor qilish", callback_data="admin_cancel_action")
    builder.adjust(1)
    return builder.as_markup()

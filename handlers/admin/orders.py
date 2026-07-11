# 📁 JOYLASHUV: aggressor_uc_bot/handlers/admin/orders.py
# ⚠ MAVJUD FAYL — to'liq almashtiring
"""
AGGRESSOR UC BOT - Admin buyurtmalar handleri.

Bu modul admin panelidagi "📦 Buyurtmalar" bo'limini va
buyurtmalarni tasdiqlash / bekor qilish / UC yuborilganini
belgilash jarayonlarini boshqaradi.
"""

from aiogram import F, Router
from aiogram.types import CallbackQuery

from database import db
from database.models import Order
from handlers.admin.panel import IsAdminFilter
from keyboards.admin_kb import (
    back_to_admin_panel_keyboard,
    order_action_keyboard,
    order_send_uc_keyboard,
    orders_filter_keyboard,
)
from keyboards.user_kb import rating_keyboard
from utils.helpers import format_datetime_display, format_price, get_username_display
from utils.texts import (
    NO_ORDERS_FOUND,
    ORDER_CANCELLED_ADMIN,
    ORDER_CANCELLED_USER,
    ORDER_COMPLETED_ADMIN,
    ORDER_COMPLETED_USER,
    ORDER_CONFIRMED_ADMIN,
    ORDER_DETAIL_ADMIN,
    ORDER_PAYMENT_CONFIRMED_USER,
    ORDERS_LIST_HEADER,
)
from utils.texts_new import RATING_REQUEST_MESSAGE

router = Router(name="admin_orders")
router.message.filter(IsAdminFilter())
router.callback_query.filter(IsAdminFilter())


def _build_order_detail_text(order) -> str:
    """Buyurtma tafsilotlarini admin uchun matn ko'rinishida tayyorlaydi."""
    username_display = get_username_display(order.username, order.telegram_id)
    return ORDER_DETAIL_ADMIN.format(
        order_id=Order.ORDER_NUMBER_OFFSET + order.id,
        username=username_display,
        telegram_id=order.telegram_id,
        pubg_uid=order.pubg_uid,
        package_name=order.package_name,
        price=format_price(order.price),
        status=order.status_display(),
        created_at=format_datetime_display(order.created_at),
    )


@router.callback_query(F.data == "admin_orders")
async def callback_admin_orders(callback: CallbackQuery) -> None:
    """"📦 Buyurtmalar" tugmasi bosilganda holat bo'yicha filtrlash menyusini chiqaradi."""
    await callback.message.edit_text(
        ORDERS_LIST_HEADER,
        reply_markup=orders_filter_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("orders_status:"))
async def callback_orders_by_status(callback: CallbackQuery) -> None:
    """Tanlangan holat bo'yicha buyurtmalar ro'yxatini chiqaradi."""
    status = callback.data.split(":")[1]
    orders = await db.get_orders_by_status(status)

    if not orders:
        await callback.message.edit_text(
            NO_ORDERS_FOUND,
            reply_markup=back_to_admin_panel_keyboard(),
        )
        await callback.answer()
        return

    await callback.answer()
    await callback.message.delete()

    for order in orders:
        text = _build_order_detail_text(order)

        if status == "pending":
            keyboard = order_action_keyboard(order.id, order.telegram_id)
        elif status == "confirmed":
            keyboard = order_send_uc_keyboard(order.id, order.telegram_id)
        else:
            keyboard = None

        if order.receipt_photo_id:
            await callback.message.answer_photo(
                photo=order.receipt_photo_id,
                caption=text,
                reply_markup=keyboard,
            )
        else:
            await callback.message.answer(text, reply_markup=keyboard)

    await callback.message.answer(
        "⬆ Yuqoridagi buyurtmalar ro'yxati.",
        reply_markup=back_to_admin_panel_keyboard(),
    )


async def _update_message_keyboard(callback: CallbackQuery, new_text: str, keyboard=None) -> None:
    """Xabar rasm (caption) yoki matn (text) ekanligiga qarab uni yangilaydi."""
    if callback.message.photo:
        await callback.message.edit_caption(caption=new_text, reply_markup=keyboard)
    else:
        await callback.message.edit_text(text=new_text, reply_markup=keyboard)


@router.callback_query(F.data.startswith("confirm_order:"))
async def callback_confirm_order(callback: CallbackQuery) -> None:
    """Admin "✅ To'lov tasdiqlandi" tugmasini bosganda ishga tushadi."""
    order_id = int(callback.data.split(":")[1])
    order = await db.get_order(order_id)

    if not order:
        await callback.answer("⚠ Buyurtma topilmadi.", show_alert=True)
        return

    if order.status != "pending":
        await callback.answer("⚠ Bu buyurtma allaqachon ko'rib chiqilgan.", show_alert=True)
        return

    await db.update_order_status(order_id, "confirmed")
    await db.add_admin_log(callback.from_user.id, "confirm_order", f"order_id={order_id}")

    try:
        await callback.bot.send_message(
            chat_id=order.telegram_id,
            text=ORDER_PAYMENT_CONFIRMED_USER.format(order_id=Order.ORDER_NUMBER_OFFSET + order.id),
        )
    except Exception:
        pass

    updated_order = await db.get_order(order_id)
    new_text = _build_order_detail_text(updated_order)
    await _update_message_keyboard(
        callback, new_text, order_send_uc_keyboard(order_id, order.telegram_id)
    )

    await callback.answer(ORDER_CONFIRMED_ADMIN.format(order_id=Order.ORDER_NUMBER_OFFSET + order_id))


@router.callback_query(F.data.startswith("cancel_order_admin:"))
async def callback_cancel_order_admin(callback: CallbackQuery) -> None:
    """Admin "❌ Bekor qilish" tugmasini bosganda ishga tushadi."""
    order_id = int(callback.data.split(":")[1])
    order = await db.get_order(order_id)

    if not order:
        await callback.answer("⚠ Buyurtma topilmadi.", show_alert=True)
        return

    if order.status in ("cancelled", "completed"):
        await callback.answer("⚠ Bu buyurtma allaqachon yakunlangan.", show_alert=True)
        return

    await db.update_order_status(order_id, "cancelled")
    await db.add_admin_log(callback.from_user.id, "cancel_order", f"order_id={order_id}")

    try:
        await callback.bot.send_message(
            chat_id=order.telegram_id,
            text=ORDER_CANCELLED_USER.format(order_id=Order.ORDER_NUMBER_OFFSET + order.id),
        )
    except Exception:
        pass

    updated_order = await db.get_order(order_id)
    new_text = _build_order_detail_text(updated_order)
    await _update_message_keyboard(callback, new_text, None)

    await callback.answer(ORDER_CANCELLED_ADMIN.format(order_id=Order.ORDER_NUMBER_OFFSET + order_id))


@router.callback_query(F.data.startswith("uc_sent:"))
async def callback_uc_sent(callback: CallbackQuery) -> None:
    """Admin "🎮 UC yuborildi" tugmasini bosganda ishga tushadi."""
    order_id = int(callback.data.split(":")[1])
    order = await db.get_order(order_id)

    if not order:
        await callback.answer("⚠ Buyurtma topilmadi.", show_alert=True)
        return

    if order.status != "confirmed":
        await callback.answer("⚠ Bu buyurtma tasdiqlangan holatda emas.", show_alert=True)
        return

    await db.update_order_status(order_id, "completed")
    await db.add_admin_log(callback.from_user.id, "uc_sent", f"order_id={order_id}")

    order_number = Order.ORDER_NUMBER_OFFSET + order.id

    try:
        await callback.bot.send_message(
            chat_id=order.telegram_id,
            text=ORDER_COMPLETED_USER.format(order_id=order_number),
        )
        # ---- YANGI: Reyting so'rovi yuborish ----
        await callback.bot.send_message(
            chat_id=order.telegram_id,
            text=RATING_REQUEST_MESSAGE.format(order_number=f"#{order_number}"),
            reply_markup=rating_keyboard(order.id),
        )
    except Exception:
        pass

    updated_order = await db.get_order(order_id)
    new_text = _build_order_detail_text(updated_order)
    await _update_message_keyboard(callback, new_text, None)

    await callback.answer(ORDER_COMPLETED_ADMIN.format(order_id=order_number))

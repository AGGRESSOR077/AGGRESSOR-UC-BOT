# 📁 JOYLASHUV: aggressor_uc_bot/handlers/user/my_orders.py
# ⚠ YANGI FAYL — ushbu nom bilan saqlang
"""
AGGRESSOR UC BOT - Buyurtmalar tarixi handleri.

Bu modul "📦 Mening buyurtmalarim" bo'limini boshqaradi:
foydalanuvchi barcha buyurtmalari va ularning holatini ko'ra oladi.
"""

from aiogram import F, Router
from aiogram.types import CallbackQuery

from database import db
from keyboards.user_kb import (
    back_to_menu_keyboard,
    my_orders_keyboard,
    order_detail_user_keyboard,
)
from utils.helpers import format_datetime_display, format_price
from utils.texts_new import (
    MY_ORDERS_EMPTY,
    MY_ORDERS_HEADER,
    ORDER_DETAIL_USER,
)

router = Router(name="user_my_orders")


@router.callback_query(F.data == "my_orders")
async def callback_my_orders(callback: CallbackQuery) -> None:
    """"📦 Mening buyurtmalarim" tugmasi bosilganda barcha buyurtmalarni chiqaradi."""
    orders = await db.get_orders_by_user(callback.from_user.id)

    if not orders:
        await callback.message.edit_text(
            MY_ORDERS_EMPTY,
            reply_markup=back_to_menu_keyboard(),
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        MY_ORDERS_HEADER,
        reply_markup=my_orders_keyboard(orders),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("view_my_order:"))
async def callback_view_my_order(callback: CallbackQuery) -> None:
    """Foydalanuvchi ro'yxatdan bitta buyurtmani tanlaganda tafsilotlarni ko'rsatadi."""
    order_id = int(callback.data.split(":")[1])
    order = await db.get_order(order_id)

    if not order or order.telegram_id != callback.from_user.id:
        await callback.answer("⚠ Buyurtma topilmadi.", show_alert=True)
        return

    show_rating = order.status == "completed" and order.rating is None

    await callback.message.edit_text(
        ORDER_DETAIL_USER.format(
            order_number=order.order_number,
            package_name=order.package_name,
            price=format_price(order.price),
            status=order.status_display(),
            rating=order.rating_display(),
            created_at=format_datetime_display(order.created_at),
        ),
        reply_markup=order_detail_user_keyboard(order.id, show_rating=show_rating),
    )
    await callback.answer()

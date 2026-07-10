"""
AGGRESSOR UC BOT - Statistika handleri.

Bu modul admin panelidagi "📊 Statistika" bo'limini boshqaradi:
bugungi daromad, bugungi buyurtmalar, jami foydalanuvchilar
va jami daromad ma'lumotlarini ko'rsatadi.
"""

from aiogram import F, Router
from aiogram.types import CallbackQuery

from database import db
from handlers.admin.panel import IsAdminFilter
from keyboards.admin_kb import back_to_admin_panel_keyboard
from utils.helpers import format_price
from utils.texts import STATISTICS_MESSAGE

router = Router(name="admin_statistics")
router.callback_query.filter(IsAdminFilter())


@router.callback_query(F.data == "admin_statistics")
async def callback_admin_statistics(callback: CallbackQuery) -> None:
    """"📊 Statistika" tugmasi bosilganda barcha statistik ma'lumotlarni chiqaradi."""
    today_income = await db.get_today_income()
    today_orders = await db.get_today_orders_count()
    total_users = await db.count_users()
    total_income = await db.get_total_income()

    await callback.message.edit_text(
        STATISTICS_MESSAGE.format(
            today_income=format_price(today_income),
            today_orders=today_orders,
            total_users=total_users,
            total_income=format_price(total_income),
        ),
        reply_markup=back_to_admin_panel_keyboard(),
    )
    await callback.answer()

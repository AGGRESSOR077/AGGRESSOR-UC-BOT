"""
AGGRESSOR UC BOT - Contact Us handleri.

Bu modul "☎ Contact Us" tugmasi bosilganda ishga tushadi
va aloqa ma'lumotlarini ko'rsatadi.
"""

from aiogram import F, Router
from aiogram.types import CallbackQuery

from config import config
from keyboards.user_kb import back_to_menu_keyboard
from utils.texts import CONTACT_US_MESSAGE

router = Router(name="user_contact")


@router.callback_query(F.data == "contact_us")
async def callback_contact_us(callback: CallbackQuery) -> None:
    """"☎ Contact Us" tugmasi bosilganda aloqa ma'lumotlarini chiqaradi."""
    phone = config.CONTACT_PHONE or "Kiritilmagan"
    username = config.CONTACT_USERNAME or "Kiritilmagan"

    await callback.message.edit_text(
        CONTACT_US_MESSAGE.format(phone=phone, username=username),
        reply_markup=back_to_menu_keyboard(),
    )
    await callback.answer()

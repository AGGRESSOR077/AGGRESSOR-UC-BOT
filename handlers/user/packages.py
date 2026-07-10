"""
AGGRESSOR UC BOT - Paketlar handleri.

Bu modul "💎 UC sotib olish" va "💰 Narxlarni ko'rish"
tugmalari bosilganda ishga tushadigan handlerlarni o'z ichiga oladi.
"""

from aiogram import F, Router
from aiogram.types import CallbackQuery

from database import db
from keyboards.user_kb import back_to_menu_keyboard, packages_keyboard
from utils.texts import (
    CHOOSE_PACKAGE_MESSAGE,
    NO_PACKAGES_AVAILABLE,
    PRICE_LIST_FOOTER,
    PRICE_LIST_HEADER,
    PRICE_LIST_ITEM,
)

router = Router(name="user_packages")


@router.callback_query(F.data == "buy_uc")
async def callback_buy_uc(callback: CallbackQuery) -> None:
    """
    "💎 UC sotib olish" tugmasi bosilganda database'dagi faol
    paketlar ro'yxatini Inline Keyboard ko'rinishida chiqaradi.
    """
    packages = await db.get_all_packages(only_active=True)

    if not packages:
        await callback.message.edit_text(
            NO_PACKAGES_AVAILABLE,
            reply_markup=back_to_menu_keyboard(),
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        CHOOSE_PACKAGE_MESSAGE,
        reply_markup=packages_keyboard(packages),
    )
    await callback.answer()


@router.callback_query(F.data == "show_prices")
async def callback_show_prices(callback: CallbackQuery) -> None:
    """
    "💰 Narxlarni ko'rish" tugmasi bosilganda barcha faol
    paketlar va ularning narxlarini matn ko'rinishida chiqaradi.
    """
    packages = await db.get_all_packages(only_active=True)

    if not packages:
        await callback.message.edit_text(
            NO_PACKAGES_AVAILABLE,
            reply_markup=back_to_menu_keyboard(),
        )
        await callback.answer()
        return

    text = PRICE_LIST_HEADER
    for package in packages:
        text += PRICE_LIST_ITEM.format(
            display_name=package.display_name(),
            price=package.display_price(),
        )
    text += PRICE_LIST_FOOTER

    await callback.message.edit_text(
        text,
        reply_markup=back_to_menu_keyboard(),
    )
    await callback.answer()

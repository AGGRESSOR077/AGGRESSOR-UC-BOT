"""
AGGRESSOR UC BOT - Buyurtma yaratish handleri.

Bu modul mijozning to'liq buyurtma jarayonini boshqaradi:
1. Paket tanlash
2. PUBG UID kiritish
3. Karta raqamini ko'rsatish
4. Chek qabul qilish
5. Buyurtmani database'ga yozish va adminga xabar yuborish
"""

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from config import config
from database import db
from keyboards.admin_kb import order_action_keyboard
from keyboards.user_kb import (
    back_to_menu_keyboard,
    cancel_order_keyboard,
    main_menu_keyboard,
)
from states.order_states import OrderStates
from utils.helpers import escape_html, format_price, get_username_display, is_valid_pubg_uid
from utils.texts import (
    NEW_ORDER_ADMIN_MESSAGE,
    ORDER_CREATED_SUCCESS,
    ORDER_ENTER_UID,
    ORDER_PAYMENT_INFO,
    ORDER_RECEIPT_INVALID,
    ORDER_UID_INVALID,
    CANCEL_ACTION,
    WELCOME_MESSAGE,
)

router = Router(name="user_order")


@router.callback_query(F.data.startswith("select_package:"))
async def callback_select_package(callback: CallbackQuery, state: FSMContext) -> None:
    """Mijoz paketni tanlaganda ishga tushadi va UID so'raydi."""
    package_id = int(callback.data.split(":")[1])
    package = await db.get_package(package_id)

    if not package or not package.is_active:
        await callback.answer("⚠ Bu paket endi mavjud emas.", show_alert=True)
        return

    await state.update_data(
        package_id=package.id,
        package_name=package.display_name(),
        uc_amount=package.uc_amount,
        price=package.price,
    )
    await state.set_state(OrderStates.waiting_for_uid)

    await callback.message.edit_text(
        ORDER_ENTER_UID.format(
            package_name=package.display_name(),
            price=package.display_price(),
        ),
        reply_markup=cancel_order_keyboard(),
    )
    await callback.answer()


@router.message(OrderStates.waiting_for_uid)
async def process_uid(message: Message, state: FSMContext) -> None:
    """Mijoz PUBG UID kiritganda ishga tushadi va to'g'riligini tekshiradi."""
    uid = (message.text or "").strip()

    if not is_valid_pubg_uid(uid):
        await message.answer(
            ORDER_UID_INVALID,
            reply_markup=cancel_order_keyboard(),
        )
        return

    data = await state.get_data()
    price = data["price"]

    card_number = await db.get_setting("card_number", config.CARD_NUMBER)
    card_owner = await db.get_setting("card_owner", config.CARD_OWNER)

    await state.update_data(pubg_uid=uid)
    await state.set_state(OrderStates.waiting_for_receipt)

    await message.answer(
        ORDER_PAYMENT_INFO.format(
            pubg_uid=uid,
            card_number=card_number,
            card_owner=card_owner,
            price=format_price(price),
        ),
        reply_markup=cancel_order_keyboard(),
    )


@router.message(OrderStates.waiting_for_receipt, F.photo)
async def process_receipt(message: Message, state: FSMContext) -> None:
    """
    Mijoz chek rasmini yuborganda ishga tushadi.

    Buyurtmani database'ga yozadi, mijozga tasdiq xabarini
    va barcha adminlarga yangi buyurtma haqida xabar yuboradi.
    """
    data = await state.get_data()

    user = await db.get_user_by_telegram_id(message.from_user.id)
    if user is None:
        await db.add_user(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            full_name=message.from_user.full_name,
        )
        user = await db.get_user_by_telegram_id(message.from_user.id)

    receipt_photo_id = message.photo[-1].file_id

    order_id = await db.create_order(
        user_id=user.id,
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        pubg_uid=data["pubg_uid"],
        package_id=data["package_id"],
        package_name=data["package_name"],
        uc_amount=data["uc_amount"],
        price=data["price"],
        receipt_photo_id=receipt_photo_id,
    )

    await message.answer(
        ORDER_CREATED_SUCCESS.format(
            order_id=order_id,
            package_name=data["package_name"],
            price=format_price(data["price"]),
        ),
        reply_markup=main_menu_keyboard(),
    )
    await state.clear()

    username_display = get_username_display(message.from_user.username, message.from_user.id)
    admin_caption = NEW_ORDER_ADMIN_MESSAGE.format(
        order_id=order_id,
        username=username_display,
        telegram_id=message.from_user.id,
        pubg_uid=data["pubg_uid"],
        package_name=data["package_name"],
        price=format_price(data["price"]),
    )

    for admin_id in config.ADMIN_IDS:
        try:
            await message.bot.send_photo(
                chat_id=admin_id,
                photo=receipt_photo_id,
                caption=admin_caption,
                reply_markup=order_action_keyboard(order_id),
            )
        except Exception:
            # Agar admin botni bloklagan bo'lsa yoki xabar yetib bormasa,
            # boshqa adminlarga yuborishda davom etamiz.
            continue


@router.message(OrderStates.waiting_for_receipt)
async def process_receipt_invalid(message: Message) -> None:
    """Agar mijoz chek o'rniga rasm bo'lmagan narsa yuborsa ishga tushadi."""
    await message.answer(
        ORDER_RECEIPT_INVALID,
        reply_markup=cancel_order_keyboard(),
    )


@router.callback_query(F.data == "cancel_order")
async def callback_cancel_order(callback: CallbackQuery, state: FSMContext) -> None:
    """Mijoz buyurtma jarayonini bekor qilganda ishga tushadi."""
    await state.clear()

    full_name_safe = escape_html(callback.from_user.full_name or "do'stim")

    await callback.message.edit_text(
        WELCOME_MESSAGE.format(full_name=full_name_safe),
        reply_markup=main_menu_keyboard(),
    )
    await callback.answer(CANCEL_ACTION)

"""
AGGRESSOR UC BOT - Admin paket boshqaruvi handleri.

Bu modul quyidagi bo'limlarni boshqaradi:
- ➕ Paket qo'shish
- ✏ Paketni tahrirlash
- ❌ Paketni o'chirish
- 💰 Narxlarni o'zgartirish
"""

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database import db
from handlers.admin.panel import IsAdminFilter
from keyboards.admin_kb import (
    admin_panel_keyboard,
    cancel_action_keyboard,
    confirm_delete_keyboard,
    package_edit_field_keyboard,
    packages_list_keyboard,
)
from states.package_states import PackageAddStates, PackageEditStates
from utils.helpers import format_price, is_valid_number, is_valid_price
from utils.texts import (
    ADMIN_PANEL_MESSAGE,
    PACKAGE_ADD_INVALID_NUMBER,
    PACKAGE_ADD_NAME,
    PACKAGE_ADD_PRICE,
    PACKAGE_ADD_SUCCESS,
    PACKAGE_ADD_UC_AMOUNT,
    PACKAGE_DELETE_CONFIRM,
    PACKAGE_DELETE_SUCCESS,
    PACKAGE_EDIT_CHOOSE_FIELD,
    PACKAGE_EDIT_ENTER_NAME,
    PACKAGE_EDIT_ENTER_PRICE,
    PACKAGE_EDIT_ENTER_UC,
    PACKAGE_EDIT_SUCCESS,
    PACKAGE_LIST_FOR_DELETE,
    PACKAGE_LIST_FOR_EDIT,
    PACKAGE_NO_PACKAGES,
)

router = Router(name="admin_packages_manage")
router.message.filter(IsAdminFilter())
router.callback_query.filter(IsAdminFilter())


# ==========================================================
# PAKET QO'SHISH
# ==========================================================

@router.callback_query(F.data == "admin_add_package")
async def callback_add_package(callback: CallbackQuery, state: FSMContext) -> None:
    """"➕ Paket qo'shish" tugmasi bosilganda paket nomini so'raydi."""
    await state.set_state(PackageAddStates.waiting_for_name)
    await callback.message.edit_text(
        PACKAGE_ADD_NAME,
        reply_markup=cancel_action_keyboard(),
    )
    await callback.answer()


@router.message(PackageAddStates.waiting_for_name)
async def process_add_package_name(message: Message, state: FSMContext) -> None:
    """Paket nomi kiritilganda UC miqdorini so'raydi."""
    name = message.text.strip()
    await state.update_data(name=name)
    await state.set_state(PackageAddStates.waiting_for_uc_amount)
    await message.answer(
        PACKAGE_ADD_UC_AMOUNT,
        reply_markup=cancel_action_keyboard(),
    )


@router.message(PackageAddStates.waiting_for_uc_amount)
async def process_add_package_uc_amount(message: Message, state: FSMContext) -> None:
    """UC miqdori kiritilganda narxni so'raydi."""
    value = message.text.strip()
    if not is_valid_number(value):
        await message.answer(
            PACKAGE_ADD_INVALID_NUMBER,
            reply_markup=cancel_action_keyboard(),
        )
        return

    await state.update_data(uc_amount=int(value))
    await state.set_state(PackageAddStates.waiting_for_price)
    await message.answer(
        PACKAGE_ADD_PRICE,
        reply_markup=cancel_action_keyboard(),
    )


@router.message(PackageAddStates.waiting_for_price)
async def process_add_package_price(message: Message, state: FSMContext) -> None:
    """Narx kiritilganda paketni database'ga qo'shadi."""
    value = message.text.strip().replace(" ", "")
    if not is_valid_price(value):
        await message.answer(
            PACKAGE_ADD_INVALID_NUMBER,
            reply_markup=cancel_action_keyboard(),
        )
        return

    data = await state.get_data()
    price = float(value)

    await db.add_package(name=data["name"], uc_amount=data["uc_amount"], price=price)
    await state.clear()

    await message.answer(
        PACKAGE_ADD_SUCCESS.format(
            name=data["name"],
            uc_amount=data["uc_amount"],
            price=format_price(price),
        ),
        reply_markup=admin_panel_keyboard(),
    )


# ==========================================================
# PAKETNI TAHRIRLASH
# ==========================================================

@router.callback_query(F.data == "admin_edit_package")
async def callback_edit_package_list(callback: CallbackQuery) -> None:
    """"✏ Paketni tahrirlash" tugmasi bosilganda paketlar ro'yxatini chiqaradi."""
    packages = await db.get_all_packages()

    if not packages:
        await callback.message.edit_text(
            PACKAGE_NO_PACKAGES,
            reply_markup=admin_panel_keyboard(),
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        PACKAGE_LIST_FOR_EDIT,
        reply_markup=packages_list_keyboard(packages, action="edit"),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("edit_pkg:"))
async def callback_edit_package_choose_field(callback: CallbackQuery) -> None:
    """Tahrirlanadigan paket tanlanganda, qaysi maydonni o'zgartirish so'raladi."""
    package_id = int(callback.data.split(":")[1])
    package = await db.get_package(package_id)

    if not package:
        await callback.answer("⚠ Paket topilmadi.", show_alert=True)
        return

    await callback.message.edit_text(
        PACKAGE_EDIT_CHOOSE_FIELD.format(name=package.display_name()),
        reply_markup=package_edit_field_keyboard(package_id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("edit_field:"))
async def callback_edit_field_choose(callback: CallbackQuery, state: FSMContext) -> None:
    """Tahrirlanadigan maydon tanlanganda, yangi qiymatni so'raydi."""
    _, field, package_id_str = callback.data.split(":")
    package_id = int(package_id_str)

    await state.update_data(edit_package_id=package_id)

    if field == "name":
        await state.set_state(PackageEditStates.waiting_for_new_name)
        prompt = PACKAGE_EDIT_ENTER_NAME
    elif field == "uc_amount":
        await state.set_state(PackageEditStates.waiting_for_new_uc_amount)
        prompt = PACKAGE_EDIT_ENTER_UC
    else:
        await state.set_state(PackageEditStates.waiting_for_new_price)
        prompt = PACKAGE_EDIT_ENTER_PRICE

    await callback.message.edit_text(prompt, reply_markup=cancel_action_keyboard())
    await callback.answer()


@router.message(PackageEditStates.waiting_for_new_name)
async def process_edit_name(message: Message, state: FSMContext) -> None:
    """Yangi paket nomi kiritilganda database'ni yangilaydi."""
    data = await state.get_data()
    package_id = data["edit_package_id"]

    await db.update_package(package_id, name=message.text.strip())
    await state.clear()

    await message.answer(PACKAGE_EDIT_SUCCESS, reply_markup=admin_panel_keyboard())


@router.message(PackageEditStates.waiting_for_new_uc_amount)
async def process_edit_uc_amount(message: Message, state: FSMContext) -> None:
    """Yangi UC miqdori kiritilganda database'ni yangilaydi."""
    value = message.text.strip()
    if not is_valid_number(value):
        await message.answer(
            PACKAGE_ADD_INVALID_NUMBER,
            reply_markup=cancel_action_keyboard(),
        )
        return

    data = await state.get_data()
    package_id = data["edit_package_id"]

    await db.update_package(package_id, uc_amount=int(value))
    await state.clear()

    await message.answer(PACKAGE_EDIT_SUCCESS, reply_markup=admin_panel_keyboard())


@router.message(PackageEditStates.waiting_for_new_price)
async def process_edit_price(message: Message, state: FSMContext) -> None:
    """Yangi narx kiritilganda database'ni yangilaydi."""
    value = message.text.strip().replace(" ", "")
    if not is_valid_price(value):
        await message.answer(
            PACKAGE_ADD_INVALID_NUMBER,
            reply_markup=cancel_action_keyboard(),
        )
        return

    data = await state.get_data()
    package_id = data["edit_package_id"]

    await db.update_package(package_id, price=float(value))
    await state.clear()

    await message.answer(PACKAGE_EDIT_SUCCESS, reply_markup=admin_panel_keyboard())


# ==========================================================
# PAKETNI O'CHIRISH
# ==========================================================

@router.callback_query(F.data == "admin_delete_package")
async def callback_delete_package_list(callback: CallbackQuery) -> None:
    """"❌ Paketni o'chirish" tugmasi bosilganda paketlar ro'yxatini chiqaradi."""
    packages = await db.get_all_packages()

    if not packages:
        await callback.message.edit_text(
            PACKAGE_NO_PACKAGES,
            reply_markup=admin_panel_keyboard(),
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        PACKAGE_LIST_FOR_DELETE,
        reply_markup=packages_list_keyboard(packages, action="delete"),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("delete_pkg:"))
async def callback_delete_package_confirm(callback: CallbackQuery) -> None:
    """O'chiriladigan paket tanlanganda, tasdiqlashni so'raydi."""
    package_id = int(callback.data.split(":")[1])
    package = await db.get_package(package_id)

    if not package:
        await callback.answer("⚠ Paket topilmadi.", show_alert=True)
        return

    await callback.message.edit_text(
        PACKAGE_DELETE_CONFIRM.format(name=package.display_name()),
        reply_markup=confirm_delete_keyboard(package_id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("confirm_delete_pkg:"))
async def callback_delete_package_execute(callback: CallbackQuery) -> None:
    """Admin o'chirishni tasdiqlaganda paketni database'dan o'chiradi."""
    package_id = int(callback.data.split(":")[1])
    await db.delete_package(package_id)

    await callback.message.edit_text(
        PACKAGE_DELETE_SUCCESS,
        reply_markup=admin_panel_keyboard(),
    )
    await callback.answer()


# ==========================================================
# NARXLARNI O'ZGARTIRISH (tezkor)
# ==========================================================

@router.callback_query(F.data == "admin_change_prices")
async def callback_change_prices_list(callback: CallbackQuery) -> None:
    """"💰 Narxlarni o'zgartirish" tugmasi bosilganda paketlar ro'yxatini chiqaradi."""
    packages = await db.get_all_packages()

    if not packages:
        await callback.message.edit_text(
            PACKAGE_NO_PACKAGES,
            reply_markup=admin_panel_keyboard(),
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        PACKAGE_LIST_FOR_EDIT,
        reply_markup=packages_list_keyboard(packages, action="change_price"),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("change_price_pkg:"))
async def callback_change_price_choose(callback: CallbackQuery, state: FSMContext) -> None:
    """Narxi o'zgartiriladigan paket tanlanganda, yangi narxni so'raydi."""
    package_id = int(callback.data.split(":")[1])
    package = await db.get_package(package_id)

    if not package:
        await callback.answer("⚠ Paket topilmadi.", show_alert=True)
        return

    await state.update_data(edit_package_id=package_id)
    await state.set_state(PackageEditStates.waiting_for_new_price)

    await callback.message.edit_text(
        PACKAGE_EDIT_ENTER_PRICE,
        reply_markup=cancel_action_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "admin_cancel_action")
async def callback_admin_cancel_action(callback: CallbackQuery, state: FSMContext) -> None:
    """Admin FSM jarayonini bekor qilib, admin panelga qaytaradi."""
    await state.clear()
    await callback.message.edit_text(
        ADMIN_PANEL_MESSAGE,
        reply_markup=admin_panel_keyboard(),
    )
    await callback.answer()

# 📁 JOYLASHUV: aggressor_uc_bot/handlers/admin/banner_management.py
# ⚠ YANGI FAYL
"""
AGGRESSOR UC BOT - Admin Banner boshqaruvi handleri.
"""

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database import db
from handlers.admin.panel import IsAdminFilter
from keyboards.admin_kb import admin_panel_keyboard, banner_menu_keyboard, skip_image_keyboard
from states.new_features_states import BannerStates
from utils.texts_new import (
    BANNER_MENU_MESSAGE,
    BANNER_NO_ACTIVE,
    BANNER_REMOVED_SUCCESS,
    BANNER_SET_ENTER_IMAGE,
    BANNER_SET_ENTER_TEXT,
    BANNER_SET_SUCCESS,
)

router = Router(name="admin_banner_management")
router.message.filter(IsAdminFilter())
router.callback_query.filter(IsAdminFilter())


@router.callback_query(F.data == "admin_banner")
async def callback_admin_banner(callback: CallbackQuery) -> None:
    active_banner = await db.get_active_banner()
    text = BANNER_MENU_MESSAGE
    if not active_banner:
        text += f"\n\n{BANNER_NO_ACTIVE}"
    else:
        text += f"\n\n🖼 Joriy banner: {active_banner.text}"

    await callback.message.edit_text(text, reply_markup=banner_menu_keyboard(bool(active_banner)))
    await callback.answer()


@router.callback_query(F.data == "banner_set")
async def callback_banner_set(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(BannerStates.waiting_for_text)
    await callback.message.edit_text(BANNER_SET_ENTER_TEXT, reply_markup=skip_image_keyboard())
    await callback.answer()


@router.message(BannerStates.waiting_for_text)
async def process_banner_text(message: Message, state: FSMContext) -> None:
    await state.update_data(banner_text=message.text.strip())
    await state.set_state(BannerStates.waiting_for_image)
    await message.answer(BANNER_SET_ENTER_IMAGE, reply_markup=skip_image_keyboard())


@router.callback_query(BannerStates.waiting_for_image, F.data == "skip_image")
async def callback_skip_banner_image(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    await db.set_banner(text=data["banner_text"], image_file_id=None)
    await db.add_admin_log(callback.from_user.id, "set_banner", "rasmsiz")
    await state.clear()
    await callback.message.edit_text(BANNER_SET_SUCCESS, reply_markup=admin_panel_keyboard())
    await callback.answer()


@router.message(BannerStates.waiting_for_image, F.photo)
async def process_banner_image(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    image_file_id = message.photo[-1].file_id
    await db.set_banner(text=data["banner_text"], image_file_id=image_file_id)
    await db.add_admin_log(message.from_user.id, "set_banner", "rasm bilan")
    await state.clear()
    await message.answer(BANNER_SET_SUCCESS, reply_markup=admin_panel_keyboard())


@router.callback_query(F.data == "banner_remove")
async def callback_banner_remove(callback: CallbackQuery) -> None:
    await db.deactivate_banner()
    await db.add_admin_log(callback.from_user.id, "remove_banner", "")
    await callback.message.edit_text(BANNER_REMOVED_SUCCESS, reply_markup=admin_panel_keyboard())
    await callback.answer()

# 📁 JOYLASHUV: aggressor_uc_bot/handlers/admin/news_management.py
# ⚠ YANGI FAYL
"""
AGGRESSOR UC BOT - Admin Yangiliklar boshqaruvi handleri.
"""

import asyncio

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database import db
from handlers.admin.panel import IsAdminFilter
from keyboards.admin_kb import (
    admin_panel_keyboard,
    confirm_delete_news_keyboard,
    news_detail_keyboard,
    news_list_keyboard,
    skip_image_keyboard,
)
from states.new_features_states import NewsCreateStates
from utils.texts_new import (
    NEWS_ADD_ENTER_IMAGE,
    NEWS_ADD_ENTER_TEXT,
    NEWS_ADD_ENTER_TITLE,
    NEWS_ADD_SUCCESS,
    NEWS_DELETE_SUCCESS,
    NEWS_LIST_EMPTY,
    NEWS_LIST_HEADER,
)

router = Router(name="admin_news_management")
router.message.filter(IsAdminFilter())
router.callback_query.filter(IsAdminFilter())


@router.callback_query(F.data == "admin_news")
async def callback_admin_news(callback: CallbackQuery) -> None:
    news_list = await db.get_all_news()
    if not news_list:
        await callback.message.edit_text(NEWS_LIST_EMPTY, reply_markup=news_list_keyboard([]))
        await callback.answer()
        return
    await callback.message.edit_text(NEWS_LIST_HEADER, reply_markup=news_list_keyboard(news_list))
    await callback.answer()


@router.callback_query(F.data == "admin_add_news")
async def callback_add_news(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(NewsCreateStates.waiting_for_title)
    await callback.message.edit_text(NEWS_ADD_ENTER_TITLE, reply_markup=skip_image_keyboard())
    await callback.answer()


@router.message(NewsCreateStates.waiting_for_title)
async def process_news_title(message: Message, state: FSMContext) -> None:
    await state.update_data(news_title=message.text.strip())
    await state.set_state(NewsCreateStates.waiting_for_text)
    await message.answer(NEWS_ADD_ENTER_TEXT, reply_markup=skip_image_keyboard())


@router.message(NewsCreateStates.waiting_for_text)
async def process_news_text(message: Message, state: FSMContext) -> None:
    await state.update_data(news_text=message.text.strip())
    await state.set_state(NewsCreateStates.waiting_for_image)
    await message.answer(NEWS_ADD_ENTER_IMAGE, reply_markup=skip_image_keyboard())


@router.callback_query(NewsCreateStates.waiting_for_image, F.data == "skip_image")
async def callback_skip_news_image(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    await db.add_news(title=data["news_title"], text=data["news_text"], image_file_id=None)
    await db.add_admin_log(callback.from_user.id, "add_news", data["news_title"])
    await state.clear()
    await callback.message.edit_text(NEWS_ADD_SUCCESS, reply_markup=admin_panel_keyboard())
    await callback.answer()


@router.message(NewsCreateStates.waiting_for_image, F.photo)
async def process_news_image(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    image_file_id = message.photo[-1].file_id
    await db.add_news(title=data["news_title"], text=data["news_text"], image_file_id=image_file_id)
    await db.add_admin_log(message.from_user.id, "add_news", data["news_title"])
    await state.clear()
    await message.answer(NEWS_ADD_SUCCESS, reply_markup=admin_panel_keyboard())


@router.callback_query(F.data.startswith("view_news:"))
async def callback_view_news(callback: CallbackQuery) -> None:
    news_id = int(callback.data.split(":")[1])
    news = await db.get_news(news_id)
    if not news:
        await callback.answer("⚠ Topilmadi.", show_alert=True)
        return

    text = f"📰 <b>{news.title}</b>\n\n{news.text}"
    await callback.message.edit_text(text, reply_markup=news_detail_keyboard(news.id))
    await callback.answer()


@router.callback_query(F.data.startswith("delete_news:"))
async def callback_delete_news_confirm(callback: CallbackQuery) -> None:
    news_id = int(callback.data.split(":")[1])
    await callback.message.edit_text(
        "❗ Ushbu yangilikni o'chirmoqchimisiz?",
        reply_markup=confirm_delete_news_keyboard(news_id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("confirm_delete_news:"))
async def callback_delete_news_execute(callback: CallbackQuery) -> None:
    news_id = int(callback.data.split(":")[1])
    await db.delete_news(news_id)
    await db.add_admin_log(callback.from_user.id, "delete_news", f"id={news_id}")
    await callback.message.edit_text(NEWS_DELETE_SUCCESS, reply_markup=admin_panel_keyboard())
    await callback.answer()


@router.callback_query(F.data.startswith("broadcast_news:"))
async def callback_broadcast_news(callback: CallbackQuery) -> None:
    news_id = int(callback.data.split(":")[1])
    news = await db.get_news(news_id)
    if not news:
        await callback.answer("⚠ Topilmadi.", show_alert=True)
        return

    telegram_ids = await db.get_all_user_telegram_ids(only_active=True)
    text = f"📰 <b>{news.title}</b>\n\n{news.text}"

    success_count = 0
    failed_count = 0
    for telegram_id in telegram_ids:
        try:
            if news.image_file_id:
                await callback.bot.send_photo(chat_id=telegram_id, photo=news.image_file_id, caption=text)
            else:
                await callback.bot.send_message(chat_id=telegram_id, text=text)
            success_count += 1
        except Exception:
            failed_count += 1
        await asyncio.sleep(0.05)

    await db.add_admin_log(callback.from_user.id, "broadcast_news", f"id={news_id}, success={success_count}")
    await callback.message.edit_text(
        f"✅ Yangilik yuborildi!\n\n✅ Muvaffaqiyatli: {success_count}\n❌ Xato: {failed_count}",
        reply_markup=admin_panel_keyboard(),
    )
    await callback.answer()

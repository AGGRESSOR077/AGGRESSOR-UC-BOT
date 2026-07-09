"""
AGGRESSOR UC BOT - Matnlar moduli.

Bu modulda botning barcha matn xabarlari saqlanadi.
Matnlarni o'zgartirish uchun faqat shu faylni tahrirlash kifoya.
"""

# ==========================================================
# UMUMIY / MIJOZ UCHUN MATNLAR
# ==========================================================

WELCOME_MESSAGE = (
    "🔥 <b>AGGRESSOR UC</b> ga xush kelibsiz, {full_name}!\n\n"
    "Bu yerda siz <b>PUBG Mobile UC</b> larni eng qulay va tezkor "
    "tarzda sotib olishingiz mumkin.\n\n"
    "✅ Tez yetkazib berish\n"
    "✅ Ishonchli va xavfsiz\n"
    "✅ 24/7 qo'llab-quvvatlash\n\n"
    "Quyidagi menyudan kerakli bo'limni tanlang 👇"
)

CHOOSE_PACKAGE_MESSAGE = "💎 <b>Quyidagi UC paketlaridan birini tanlang:</b>"

NO_PACKAGES_AVAILABLE = (
    "😔 Hozircha mavjud paketlar yo'q.\n"
    "Iltimos, keyinroq qayta urinib ko'ring."
)

PRICE_LIST_HEADER = "💰 <b>Mavjud UC paketlari va narxlari:</b>\n\n"
PRICE_LIST_ITEM = "🔹 {display_name} — <b>{price}</b>\n"
PRICE_LIST_FOOTER = "\nSotib olish uchun \"💎 UC sotib olish\" tugmasini bosing."

CONTACT_US_MESSAGE = (
    "☎ <b>Biz bilan bog'lanish</b>\n\n"
    "📞 Telefon: {phone}\n"
    "💬 Telegram: {username}\n\n"
    "Savollaringiz bo'lsa, biz bilan bemalol bog'laning!"
)

ORDER_ENTER_UID = (
    "🎮 Siz tanladingiz: <b>{package_name}</b>\n"
    "💰 Narxi: <b>{price}</b>\n\n"
    "Endi PUBG Mobile <b>UID</b> raqamingizni kiriting.\n"
    "(UID — bu sizning o'yin ichidagi shaxsiy ID raqamingiz, "
    "PUBG Mobile profilingizda ko'rsatilgan)"
)

ORDER_UID_INVALID = (
    "⚠ Noto'g'ri UID format.\n"
    "UID faqat raqamlardan iborat bo'lishi kerak (masalan: 5123456789).\n"
    "Iltimos, qaytadan kiriting."
)

ORDER_PAYMENT_INFO = (
    "✅ UID qabul qilindi: <code>{pubg_uid}</code>\n\n"
    "💳 <b>To'lov uchun karta ma'lumotlari:</b>\n\n"
    "Karta raqami: <code>{card_number}</code>\n"
    "Karta egasi: <b>{card_owner}</b>\n"
    "To'lov summasi: <b>{price}</b>\n\n"
    "To'lovni amalga oshirgach, chek (skrinshot) rasmini shu yerga yuboring."
)

ORDER_RECEIPT_INVALID = (
    "⚠ Iltimos, chek rasmini (skrinshot) rasm shaklida yuboring.\n"
    "Matn emas, aynan rasm bo'lishi kerak."
)

ORDER_CREATED_SUCCESS = (
    "✅ <b>Buyurtmangiz qabul qilindi!</b>\n\n"
    "🆔 Buyurtma raqami: <b>#{order_id}</b>\n"
    "🎮 Paket: {package_name}\n"
    "💰 Narxi: {price}\n\n"
    "Admin tekshiruvidan so'ng sizga xabar beriladi.\n"
    "Iltimos, kuting ⏳"
)

ORDER_PAYMENT_CONFIRMED_USER = (
    "✅ <b>To'lovingiz tasdiqlandi.</b>\n\n"
    "🆔 Buyurtma: #{order_id}\n"
    "Tez orada UC hisobingizga o'tkaziladi 🎮"
)

ORDER_CANCELLED_USER = (
    "❌ <b>Buyurtmangiz bekor qilindi.</b>\n\n"
    "🆔 Buyurtma: #{order_id}\n\n"
    "Agar bu xato deb hisoblasangiz, biz bilan bog'laning."
)

ORDER_COMPLETED_USER = (
    "🎮 <b>UC muvaffaqiyatli yuborildi!</b>\n\n"
    "🆔 Buyurtma: #{order_id}\n"
    "🎉 PUBG Mobile hisobingizni tekshiring.\n\n"
    "Xizmatimizdan foydalanganingiz uchun rahmat! ❤️"
)

# ==========================================================
# ADMIN UCHUN MATNLAR
# ==========================================================

ADMIN_PANEL_MESSAGE = "⚙ <b>Admin panelga xush kelibsiz!</b>\n\nKerakli bo'limni tanlang 👇"

NOT_ADMIN_MESSAGE = "⛔ Sizda bu buyruqni bajarish uchun ruxsat yo'q."

NEW_ORDER_ADMIN_MESSAGE = (
    "🆕 <b>Yangi buyurtma!</b>\n\n"
    "🆔 Buyurtma ID: #{order_id}\n"
    "👤 Username: {username}\n"
    "🆔 Telegram ID: <code>{telegram_id}</code>\n"
    "🎮 PUBG UID: <code>{pubg_uid}</code>\n"
    "📦 Paket: {package_name}\n"
    "💰 Narx: {price}\n"
)

ORDER_CONFIRMED_ADMIN = "✅ Buyurtma #{order_id} tasdiqlandi. Endi UC yuborishingiz kerak."
ORDER_CANCELLED_ADMIN = "❌ Buyurtma #{order_id} bekor qilindi."
ORDER_COMPLETED_ADMIN = "🎮 Buyurtma #{order_id} bajarildi deb belgilandi."

ORDERS_LIST_HEADER = "📦 <b>Buyurtmalar ro'yxati</b>\n\nHolatni tanlang:"
NO_ORDERS_FOUND = "📭 Bu bo'limda buyurtmalar topilmadi."

ORDER_DETAIL_ADMIN = (
    "🆔 Buyurtma ID: #{order_id}\n"
    "👤 Username: {username}\n"
    "🆔 Telegram ID: <code>{telegram_id}</code>\n"
    "🎮 PUBG UID: <code>{pubg_uid}</code>\n"
    "📦 Paket: {package_name}\n"
    "💰 Narx: {price}\n"
    "📌 Holat: {status}\n"
    "🕒 Sana: {created_at}\n"
)

# ---- Paket boshqaruvi ----

PACKAGE_ADD_NAME = "➕ Yangi paket nomini kiriting (masalan: Standart, Aksiya, va h.k.):"
PACKAGE_ADD_UC_AMOUNT = "🔢 UC miqdorini kiriting (faqat raqam, masalan: 660):"
PACKAGE_ADD_PRICE = "💰 Narxini kiriting (so'mda, faqat raqam, masalan: 150000):"
PACKAGE_ADD_INVALID_NUMBER = "⚠ Iltimos, faqat raqam kiriting."
PACKAGE_ADD_SUCCESS = (
    "✅ Yangi paket qo'shildi!\n\n"
    "📦 Nomi: {name}\n"
    "🔢 UC: {uc_amount}\n"
    "💰 Narx: {price}"
)

PACKAGE_LIST_FOR_EDIT = "✏ Tahrirlash uchun paketni tanlang:"
PACKAGE_LIST_FOR_DELETE = "❌ O'chirish uchun paketni tanlang:"
PACKAGE_NO_PACKAGES = "📭 Hozircha hech qanday paket mavjud emas."

PACKAGE_EDIT_CHOOSE_FIELD = (
    "✏ <b>{name}</b> paketini tahrirlash.\n\n"
    "Qaysi maydonni o'zgartirmoqchisiz?"
)
PACKAGE_EDIT_ENTER_NAME = "✏ Yangi nomni kiriting:"
PACKAGE_EDIT_ENTER_UC = "✏ Yangi UC miqdorini kiriting:"
PACKAGE_EDIT_ENTER_PRICE = "✏ Yangi narxni kiriting:"
PACKAGE_EDIT_SUCCESS = "✅ Paket muvaffaqiyatli yangilandi!"

PACKAGE_DELETE_CONFIRM = "❗ Rostdan ham <b>{name}</b> paketini o'chirmoqchimisiz?"
PACKAGE_DELETE_SUCCESS = "✅ Paket muvaffaqiyatli o'chirildi."
PACKAGE_DELETE_CANCELLED = "🚫 O'chirish bekor qilindi."

# ---- Statistika ----

STATISTICS_MESSAGE = (
    "📊 <b>Statistika</b>\n\n"
    "📅 Bugungi daromad: <b>{today_income}</b>\n"
    "🧾 Bugungi buyurtmalar: <b>{today_orders}</b>\n"
    "👥 Jami foydalanuvchilar: <b>{total_users}</b>\n"
    "💰 Jami daromad: <b>{total_income}</b>\n"
)

# ---- Broadcast ----

BROADCAST_ENTER_MESSAGE = (
    "📢 Barcha foydalanuvchilarga yuboriladigan xabar matnini kiriting.\n\n"
    "Bekor qilish uchun /cancel buyrug'ini yuboring."
)
BROADCAST_CONFIRM = (
    "📢 <b>Quyidagi xabar yuboriladi:</b>\n\n"
    "{text}\n\n"
    "Jami <b>{count}</b> ta foydalanuvchiga yuborilsinmi?"
)
BROADCAST_STARTED = "📤 Xabar yuborish boshlandi, iltimos kuting..."
BROADCAST_FINISHED = (
    "✅ <b>Broadcast yakunlandi!</b>\n\n"
    "✅ Yuborildi: {success}\n"
    "❌ Yuborilmadi: {failed}"
)
BROADCAST_CANCELLED = "🚫 Broadcast bekor qilindi."

# ---- Sozlamalar ----

SETTINGS_MENU_MESSAGE = "⚙ <b>Sozlamalar</b>\n\nO'zgartirmoqchi bo'lgan sozlamani tanlang:"
SETTINGS_CURRENT_CARD = (
    "💳 <b>Joriy karta ma'lumotlari:</b>\n\n"
    "Karta raqami: <code>{card_number}</code>\n"
    "Karta egasi: <b>{card_owner}</b>"
)
SETTINGS_ENTER_CARD_NUMBER = "💳 Yangi karta raqamini kiriting:"
SETTINGS_ENTER_CARD_OWNER = "👤 Karta egasining F.I.Sh ni kiriting:"
SETTINGS_UPDATED_SUCCESS = "✅ Sozlamalar muvaffaqiyatli yangilandi!"

# ---- Umumiy tugmalar / holatlar ----

CANCEL_ACTION = "🚫 Amal bekor qilindi."
BACK_TO_MENU = "⬅ Asosiy menyuga qaytdingiz."
OPERATION_ERROR = "⚠ Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring."

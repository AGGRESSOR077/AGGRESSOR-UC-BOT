"""
AGGRESSOR UC BOT - Yangi funksiyalar uchun matnlar moduli.

Bu modul upgrade doirasida qo'shilgan barcha yangi bo'limlar uchun
matnlarni o'z ichiga oladi. Mavjud `utils/texts.py` fayli
o'zgartirilmagan — bu fayl faqat qo'shimcha matnlarni ta'minlaydi.
"""

# ==========================================================
# BUYURTMALAR TARIXI
# ==========================================================

MY_ORDERS_HEADER = "📦 <b>Mening buyurtmalarim</b>\n\nQuyida barcha buyurtmalaringiz ro'yxati:"
MY_ORDERS_EMPTY = "📭 Sizda hali birorta ham buyurtma yo'q."
MY_ORDERS_ITEM = (
    "🆔 Buyurtma: <b>{order_number}</b>\n"
    "📦 Paket: {package_name}\n"
    "💰 Narx: {price}\n"
    "📌 Holat: {status}\n"
    "🕒 Sana: {created_at}\n"
)

ORDER_DETAIL_USER = (
    "🆔 Buyurtma: <b>{order_number}</b>\n"
    "📦 Paket: {package_name}\n"
    "💰 Narx: {price}\n"
    "📌 Holat: {status}\n"
    "⭐ Baho: {rating}\n"
    "🕒 Sana: {created_at}\n"
)

# ==========================================================
# REYTING (1-5 ⭐)
# ==========================================================

RATING_REQUEST_MESSAGE = (
    "🎮 Buyurtmangiz <b>{order_number}</b> muvaffaqiyatli yakunlandi!\n\n"
    "Xizmatimizni baholab bera olasizmi? ⭐"
)
RATING_THANKS_MESSAGE = "🙏 Bahoyingiz uchun rahmat! ({rating} ⭐)"
RATING_ALREADY_RATED = "✅ Siz bu buyurtmaga allaqachon baho bergansiz."

# ==========================================================
# PROMO KOD
# ==========================================================

PROMO_ENTER_CODE_PROMPT = "🎁 Promo kodingiz bo'lsa kiriting, aks holda o'tkazib yuborish uchun \"⏭ O'tkazib yuborish\" tugmasini bosing."
PROMO_CODE_INVALID = "⚠ Bunday promo kod topilmadi yoki muddati o'tgan."
PROMO_CODE_ALREADY_USED = "⚠ Siz bu promo koddan avval foydalangansiz."
PROMO_CODE_APPLIED = (
    "✅ Promo kod qabul qilindi!\n\n"
    "🎁 {promo_description}\n"
    "💰 Yangi narx: <b>{new_price}</b>"
)
PROMO_CODE_SKIPPED = "⏭ Promo kodsiz davom etilmoqda."

PROMO_ADMIN_ENTER_CODE = "🎁 Yangi promo kod nomini kiriting (masalan: SUMMER2026):"
PROMO_ADMIN_CODE_EXISTS = "⚠ Bunday promo kod allaqachon mavjud. Boshqa nom kiriting."
PROMO_ADMIN_CHOOSE_TYPE = "🎯 Promo turini tanlang:"
PROMO_ADMIN_ENTER_PERCENT = "🔢 Chegirma foizini kiriting (masalan: 15):"
PROMO_ADMIN_ENTER_AMOUNT = "💰 Chegirma summasini kiriting (so'mda):"
PROMO_ADMIN_ENTER_FREE_UC = "🎮 Bepul beriladigan UC miqdorini kiriting:"
PROMO_ADMIN_ENTER_MAX_USES = "🔢 Maksimal foydalanish sonini kiriting (cheklovsiz uchun 0 kiriting):"
PROMO_ADMIN_ENTER_EXPIRY = "📅 Amal qilish muddatini kunlarda kiriting (masalan: 30). Cheksiz uchun 0 kiriting:"
PROMO_ADMIN_CREATED_SUCCESS = (
    "✅ Promo kod yaratildi!\n\n"
    "🎁 Kod: <code>{code}</code>\n"
    "🎯 Turi: {type_display}\n"
    "🔢 Maksimal foydalanish: {max_uses}\n"
    "📅 Muddati: {expiry_display}"
)
PROMO_LIST_HEADER = "🎁 <b>Promo kodlar ro'yxati:</b>"
PROMO_LIST_EMPTY = "📭 Hozircha promo kodlar mavjud emas."
PROMO_DETAIL_ADMIN = (
    "🎁 Kod: <code>{code}</code>\n"
    "🎯 Turi: {type_display}\n"
    "🔢 Ishlatilgan: {used_count}/{max_uses_display}\n"
    "📌 Holat: {status_display}\n"
    "📅 Muddati: {expiry_display}\n"
)
PROMO_DELETED_SUCCESS = "✅ Promo kod o'chirildi."
PROMO_ACTIVATED = "✅ Promo kod yoqildi."
PROMO_DEACTIVATED = "🚫 Promo kod o'chirildi (nofaol)."

# ==========================================================
# REFERRAL TIZIMI
# ==========================================================

REFERRAL_MENU_MESSAGE = (
    "🤝 <b>Referral tizimi</b>\n\n"
    "Do'stlaringizni taklif qiling va bonuslar qo'lga kiriting!\n\n"
    "🔗 Sizning havolangiz:\n<code>{referral_link}</code>\n\n"
    "👥 Taklif qilganlar: <b>{referrals_count}</b> ta\n"
    "💰 Bonus balansi: <b>{bonus_balance}</b>\n\n"
    "{threshold_info}"
)
REFERRAL_THRESHOLD_INFO = "🎯 {threshold_count} ta taklif qilsangiz — UC narxiga {threshold_percent}% chegirma olasiz!"
REFERRAL_THRESHOLD_REACHED = "🎉 Tabriklaymiz! Siz {threshold_count} ta referral chegarasiga yetdingiz — endi UC narxiga {threshold_percent}% chegirma olasiz!"
REFERRAL_DISABLED_MESSAGE = "😔 Referral tizimi hozircha faol emas."
REFERRAL_BONUS_RECEIVED = (
    "🎉 Sizning havolangiz orqali yangi foydalanuvchi qo'shildi!\n"
    "💰 Bonusingiz: <b>{bonus_amount}</b>"
)
REFERRAL_WELCOME_BONUS_INFO = "🤝 Siz {referrer_name} tomonidan taklif qilindingiz!"

REFERRAL_SETTINGS_MESSAGE = (
    "🤝 <b>Referral sozlamalari</b>\n\n"
    "📌 Holati: {status}\n"
    "💰 Minimal buyurtma summasi: {min_order}\n"
    "🎁 Taklif bonusi turi: {bonus_type_display}\n"
    "🎁 Bonus qiymati: {bonus_value}\n"
    "🎯 Chegara: {threshold_count} ta = {threshold_percent}% chegirma"
)
REFERRAL_SETTINGS_ENTER_MIN_ORDER = "💰 Minimal buyurtma summasini kiriting (so'mda):"
REFERRAL_SETTINGS_ENTER_BONUS_VALUE = "🎁 Bonus qiymatini kiriting:"
REFERRAL_SETTINGS_ENTER_THRESHOLD_COUNT = "🎯 Chegara sonini kiriting (masalan: 20):"
REFERRAL_SETTINGS_ENTER_THRESHOLD_PERCENT = "🎯 Chegaradan keyingi chegirma foizini kiriting (masalan: 15):"
REFERRAL_SETTINGS_UPDATED = "✅ Referral sozlamalari yangilandi!"
REFERRAL_ENABLED = "✅ Referral tizimi yoqildi."
REFERRAL_DISABLED = "🚫 Referral tizimi o'chirildi."

# ==========================================================
# AVTOMATIK BEKOR QILISH (Auto Cancel)
# ==========================================================

ORDER_AUTO_CANCELLED_USER = (
    "⏰ <b>Buyurtmangiz avtomatik bekor qilindi.</b>\n\n"
    "🆔 Buyurtma: {order_number}\n"
    "Sababi: Belgilangan vaqt ichida to'lov cheki yuborilmadi.\n\n"
    "Agar hali ham xarid qilishni istasangiz, qaytadan buyurtma bering."
)
ORDER_AUTO_CANCELLED_ADMIN_LOG = "Buyurtma {order_number} chek yuborilmagani sababli avtomatik bekor qilindi."

# ==========================================================
# BANNER
# ==========================================================

BANNER_SET_ENTER_TEXT = "🖼 Banner matnini kiriting:"
BANNER_SET_ENTER_IMAGE = (
    "🖼 Banner uchun rasm yuboring (ixtiyoriy).\n"
    "Agar rasm kerak bo'lmasa, \"⏭ O'tkazib yuborish\" tugmasini bosing."
)
BANNER_SET_SUCCESS = "✅ Banner muvaffaqiyatli o'rnatildi!"
BANNER_REMOVED_SUCCESS = "✅ Banner olib tashlandi."
BANNER_MENU_MESSAGE = "🖼 <b>Banner boshqaruvi</b>"
BANNER_NO_ACTIVE = "📭 Hozircha faol banner mavjud emas."

# ==========================================================
# YANGILIKLAR
# ==========================================================

NEWS_ADD_ENTER_TITLE = "📰 Yangilik sarlavhasini kiriting:"
NEWS_ADD_ENTER_TEXT = "📰 Yangilik matnini kiriting:"
NEWS_ADD_ENTER_IMAGE = (
    "🖼 Yangilik uchun rasm yuboring (ixtiyoriy).\n"
    "Agar rasm kerak bo'lmasa, \"⏭ O'tkazib yuborish\" tugmasini bosing."
)
NEWS_ADD_SUCCESS = "✅ Yangilik muvaffaqiyatli qo'shildi!"
NEWS_LIST_HEADER = "📰 <b>Yangiliklar ro'yxati</b>"
NEWS_LIST_EMPTY = "📭 Hozircha yangiliklar mavjud emas."
NEWS_DELETE_SUCCESS = "✅ Yangilik o'chirildi."
NEWS_EDIT_SUCCESS = "✅ Yangilik yangilandi."
NEWS_BROADCAST_TO_USERS = "📢 Bu yangilikni barcha foydalanuvchilarga yuborilsinmi?"

# ==========================================================
# TO'LOV USULLARI
# ==========================================================

PAYMENT_METHOD_ADD_ENTER_NAME = "💳 To'lov usuli nomini kiriting (masalan: Uzcard, Humo, Visa):"
PAYMENT_METHOD_ADD_ENTER_CARD_NUMBER = "💳 Karta raqamini kiriting:"
PAYMENT_METHOD_ADD_ENTER_CARD_OWNER = "👤 Karta egasi F.I.Sh ni kiriting:"
PAYMENT_METHOD_ADD_SUCCESS = "✅ Yangi to'lov usuli qo'shildi!"
PAYMENT_METHOD_LIST_HEADER = "💳 <b>To'lov usullari</b>"
PAYMENT_METHOD_LIST_EMPTY = "📭 Hozircha to'lov usullari mavjud emas."
PAYMENT_METHOD_DELETE_SUCCESS = "✅ To'lov usuli o'chirildi."
PAYMENT_METHOD_CHOOSE_PROMPT = "💳 To'lov usulini tanlang:"

# ==========================================================
# UC CALCULATOR
# ==========================================================

UC_CALCULATOR_PROMPT = (
    "🧮 <b>UC Kalkulyator</b>\n\n"
    "UC miqdorini (masalan: 660) yoki narxni so'm ko'rinishida "
    "(masalan: 150000so'm) kiriting — men avtomatik hisoblab beraman."
)
UC_CALCULATOR_RESULT_BY_UC = (
    "🧮 <b>{uc_amount} UC</b> narxi taxminan: <b>{price}</b>\n\n"
    "(1 UC ≈ {rate_per_uc} so'm bo'yicha hisoblandi)"
)
UC_CALCULATOR_RESULT_BY_PRICE = (
    "🧮 <b>{price}</b> summasiga taxminan <b>{uc_amount} UC</b> sotib olish mumkin.\n\n"
    "(1 UC ≈ {rate_per_uc} so'm bo'yicha hisoblandi)"
)
UC_CALCULATOR_INVALID_INPUT = "⚠ Iltimos, faqat raqam kiriting (UC miqdori yoki narx)."
UC_CALCULATOR_NO_RATE = "⚠ Hozircha hisoblash uchun yetarli ma'lumot yo'q. Iltimos, mavjud paketlarni ko'ring."

# ==========================================================
# BAN TIZIMI
# ==========================================================

BAN_ENTER_REASON = "🚫 Foydalanuvchini ban qilish sababini kiriting:"
BAN_SUCCESS_ADMIN = "✅ Foydalanuvchi ban qilindi."
BAN_SUCCESS_USER = (
    "🚫 <b>Siz botdan foydalanish huquqidan mahrum qilindingiz.</b>\n\n"
    "Sabab: {reason}\n\n"
    "Agar bu xato deb hisoblasangiz, qo'llab-quvvatlash xizmatiga murojaat qiling."
)
UNBAN_SUCCESS_ADMIN = "✅ Foydalanuvchi bandan chiqarildi."
UNBAN_SUCCESS_USER = "✅ Siz bandan chiqarildingiz. Botdan qaytadan foydalanishingiz mumkin."
USER_IS_BANNED_MESSAGE = "🚫 Siz botdan foydalanish huquqidan mahrum qilingansiz.\n\nSabab: {reason}"

# ==========================================================
# BLACKLIST
# ==========================================================

BLACKLIST_ADD_SUCCESS = "✅ Foydalanuvchi qora ro'yxatga qo'shildi."
BLACKLIST_REMOVE_SUCCESS = "✅ Foydalanuvchi qora ro'yxatdan chiqarildi."

# ==========================================================
# ANTI SPAM
# ==========================================================

ANTI_SPAM_WARNING = "⏳ Siz juda tez-tez so'rov yubormoqdasiz. Iltimos, biroz kuting."
ANTI_SPAM_TEMP_RESTRICTED = (
    "🚫 Siz vaqtincha cheklandingiz.\n"
    "Iltimos, {seconds} soniyadan so'ng qaytadan urinib ko'ring."
)

# ==========================================================
# FOYDALANUVCHILAR (Admin panel, pagination)
# ==========================================================

USERS_LIST_HEADER = "👥 <b>Foydalanuvchilar</b>\n\nSahifa: {current_page}/{total_pages}"
USERS_LIST_ITEM = "{index}. {full_name} | @{username} | ID: <code>{telegram_id}</code>"
USERS_LIST_EMPTY = "📭 Hozircha foydalanuvchilar mavjud emas."

USER_PROFILE_MESSAGE = (
    "👤 <b>Foydalanuvchi profili</b>\n\n"
    "📝 Ism: {full_name}\n"
    "🔗 Username: @{username}\n"
    "🆔 Telegram ID: <code>{telegram_id}</code>\n"
    "📦 Buyurtmalar soni: {orders_count}\n"
    "💰 Umumiy xarid: {total_spent}\n"
    "🕐 Birinchi buyurtma: {first_order}\n"
    "🕐 Oxirgi buyurtma: {last_order}\n"
    "📌 Holati: {status}\n"
)

USER_MESSAGE_ENTER_TEXT = "📨 Foydalanuvchiga yuboriladigan xabar matnini kiriting:"
USER_MESSAGE_SENT_SUCCESS = "✅ Xabar foydalanuvchiga yuborildi."
USER_MESSAGE_SEND_FAILED = "⚠ Xabarni yuborib bo'lmadi (foydalanuvchi botni bloklagan bo'lishi mumkin)."
USER_MESSAGE_RECEIVED_PREFIX = "📨 <b>Admin tomonidan xabar:</b>\n\n{text}"

# ==========================================================
# KENGAYTIRILGAN STATISTIKA
# ==========================================================

STATISTICS_EXTENDED_MESSAGE = (
    "📊 <b>Statistika</b>\n\n"
    "📅 Bugungi buyurtmalar: <b>{today_orders}</b>\n"
    "📦 Jami buyurtmalar: <b>{total_orders}</b>\n"
    "💵 Bugungi daromad: <b>{today_income}</b>\n"
    "💰 Jami daromad: <b>{total_income}</b>\n\n"
    "🏆 <b>Eng faol xaridorlar:</b>\n{top_buyers}\n\n"
    "🔥 <b>Eng ko'p sotilgan paketlar:</b>\n{top_packages}"
)
STATISTICS_TOP_BUYER_ITEM = "{index}. @{username} — {orders_count} ta buyurtma, {total_spent}\n"
STATISTICS_TOP_PACKAGE_ITEM = "{index}. {package_name} — {sold_count} marta sotilgan\n"
STATISTICS_NO_DATA = "Hozircha ma'lumot yo'q"

# ==========================================================
# TUG'ILGAN KUN
# ==========================================================

BIRTHDAY_GREETING_MESSAGE = (
    "🎉 <b>Tug'ilgan kuningiz muborak bo'lsin, {full_name}!</b>\n\n"
    "Sizga baxt, sog'lik va omad tilaymiz! 🎂\n\n"
    "Sovg'a sifatida sizga <b>{bonus_amount}</b> bonus taqdim etamiz! 🎁"
)

# ==========================================================
# ADMIN LOG
# ==========================================================

ADMIN_LOGS_HEADER = "📋 <b>So'nggi admin amallari</b>"
ADMIN_LOGS_ITEM = "🕐 {created_at} — Admin <code>{admin_telegram_id}</code>: {action} {details}\n"
ADMIN_LOGS_EMPTY = "📭 Hali hech qanday amal qayd etilmagan."

# ==========================================================
# BROADCAST (media qo'llab-quvvatlash)
# ==========================================================

BROADCAST_MEDIA_RECEIVED = "📢 Media xabar qabul qilindi. Yuborishni tasdiqlaysizmi?"

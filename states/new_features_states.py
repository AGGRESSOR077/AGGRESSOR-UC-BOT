"""
AGGRESSOR UC BOT - Yangi funksiyalar uchun FSM holatlari.

Bu modul upgrade doirasida qo'shilgan barcha yangi bo'limlar
(Promo kod, Ban, Banner, Yangiliklar, To'lov usullari, Referral
sozlamalari, Admin xabar yuborish, UC Calculator) uchun FSM
holatlarini o'z ichiga oladi.

Mavjud `states/order_states.py`, `states/package_states.py` va
`states/admin_states.py` fayllari o'zgartirilmagan — bu fayl
faqat qo'shimcha holatlarni ta'minlaydi.
"""

from aiogram.fsm.state import State, StatesGroup


class PromoCreateStates(StatesGroup):
    """
    Admin tomonidan yangi promo kod yaratish jarayonidagi holatlar:

    1. waiting_for_code        -> Promo kod nomi kutilmoqda
    2. waiting_for_type        -> Promo turi tanlanishi kutilmoqda
    3. waiting_for_percent     -> Foiz miqdori kutilmoqda (agar "percent" tanlansa)
    4. waiting_for_amount      -> Summasi kutilmoqda (agar "fixed" tanlansa)
    5. waiting_for_free_uc     -> UC miqdori kutilmoqda (agar "free_uc" tanlansa)
    6. waiting_for_max_uses    -> Maksimal foydalanish soni kutilmoqda
    7. waiting_for_expiry      -> Amal qilish muddati (kun) kutilmoqda
    """

    waiting_for_code = State()
    waiting_for_type = State()
    waiting_for_percent = State()
    waiting_for_amount = State()
    waiting_for_free_uc = State()
    waiting_for_max_uses = State()
    waiting_for_expiry = State()


class PromoEditStates(StatesGroup):
    """Mavjud promo kodni tahrirlash jarayonidagi holatlar."""

    waiting_for_new_max_uses = State()
    waiting_for_new_expiry = State()


class PromoApplyStates(StatesGroup):
    """Mijoz buyurtma paytida promo kod kiritish jarayonidagi holat."""

    waiting_for_code = State()


class BanStates(StatesGroup):
    """
    Admin foydalanuvchini ban qilish jarayonidagi holat:

    waiting_for_reason -> Ban sababi kutilmoqda
    """

    waiting_for_reason = State()


class BannerStates(StatesGroup):
    """
    Admin banner o'rnatish jarayonidagi holatlar:

    1. waiting_for_text  -> Banner matni kutilmoqda
    2. waiting_for_image -> Banner rasmi kutilmoqda (ixtiyoriy)
    """

    waiting_for_text = State()
    waiting_for_image = State()


class NewsCreateStates(StatesGroup):
    """
    Admin yangi yangilik/aksiya yaratish jarayonidagi holatlar:

    1. waiting_for_title -> Sarlavha kutilmoqda
    2. waiting_for_text  -> Matn kutilmoqda
    3. waiting_for_image -> Rasm kutilmoqda (ixtiyoriy)
    """

    waiting_for_title = State()
    waiting_for_text = State()
    waiting_for_image = State()


class NewsEditStates(StatesGroup):
    """Mavjud yangilikni tahrirlash jarayonidagi holatlar."""

    waiting_for_new_title = State()
    waiting_for_new_text = State()


class PaymentMethodCreateStates(StatesGroup):
    """
    Admin yangi to'lov usuli (karta) qo'shish jarayonidagi holatlar:

    1. waiting_for_name        -> To'lov usuli nomi (masalan: "Uzcard")
    2. waiting_for_card_number -> Karta raqami
    3. waiting_for_card_owner  -> Karta egasi F.I.Sh
    """

    waiting_for_name = State()
    waiting_for_card_number = State()
    waiting_for_card_owner = State()


class PaymentMethodEditStates(StatesGroup):
    """Mavjud to'lov usulini tahrirlash jarayonidagi holatlar."""

    waiting_for_new_name = State()
    waiting_for_new_card_number = State()
    waiting_for_new_card_owner = State()


class ReferralSettingsStates(StatesGroup):
    """
    Admin referral tizimi sozlamalarini o'zgartirish jarayonidagi holatlar:

    1. waiting_for_min_order       -> Minimal buyurtma summasi
    2. waiting_for_bonus_value     -> Taklif bonusi qiymati
    3. waiting_for_threshold_count -> Chegara son (masalan: 20 ta referral)
    4. waiting_for_threshold_percent -> Chegaradan keyingi chegirma foizi
    """

    waiting_for_min_order = State()
    waiting_for_bonus_value = State()
    waiting_for_threshold_count = State()
    waiting_for_threshold_percent = State()


class AdminMessageUserStates(StatesGroup):
    """
    Admin foydalanuvchilar bo'limidan bitta foydalanuvchiga xabar
    yuborish jarayonidagi holat.
    """

    waiting_for_message = State()


class UCCalculatorStates(StatesGroup):
    """
    UC Calculator jarayonidagi holat: foydalanuvchi UC miqdori yoki
    narx kiritganda avtomatik hisoblash uchun kutish holati.
    """

    waiting_for_input = State()

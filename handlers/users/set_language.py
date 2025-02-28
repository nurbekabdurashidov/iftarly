import asyncio
import asyncio
from loader import dp, bot
from aiogram.filters import Command, CommandStart
from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
import aiohttp
from api import get_user, create_user, change_user_language
from keyboards.default.buttons import prayer_times_buttons
import base64
import io
from aiogram.types import BufferedInputFile, InlineKeyboardMarkup
import aiohttp
from loader import dp,bot
from aiogram.filters import Command
from aiogram import types
from api import get_user,change_user_language
from keyboards.inline.buttons import LanguageCallback,language_button
from keyboards.default.buttons import prayer_times_buttons
@dp.message(Command('set_language'))
async def setlanguage(message:types.Message):
    user = get_user(telegram_id=message.from_user.id)
    if user !='Not Found':
        language = user.get('language','uz')
    else:
        language = 'uz'
    text ="Kerakli tilni tanlang" if language=='uz' else "Choose language"
    await message.answer(text,reply_markup=language_button())
    await message.delete()
@dp.callback_query(LanguageCallback.filter())
async def change_language(call:types.CallbackQuery,callback_data:LanguageCallback):
    await call.answer(cache_time=60)
    language = callback_data.language
    change_user_language(telegram_id=call.from_user.id,language=language)
    text = "Yangi til sozlandi" if language == 'uz' else "Language updated"
    data  = await call.message.answer(text,reply_markup=prayer_times_buttons(language))

REGIONS = {
    "tashkent": {"uz": "Toshkent", "en": "Tashkent", "ru": "Ташкент"},
    "samarkand": {"uz": "Samarqand", "en": "Samarkand", "ru": "Самарканд"},
    "bukhara": {"uz": "Buxoro", "en": "Bukhara", "ru": "Бухара"},
    "fergana": {"uz": "Farg‘ona", "en": "Fergana", "ru": "Фергана"},
    "andijan": {"uz": "Andijon", "en": "Andijan", "ru": "Андижан"},
    "namangan": {"uz": "Namangan", "en": "Namangan", "ru": "Наманган"},
    "khorezm": {"uz": "Xorazm", "en": "Khorezm", "ru": "Хорезм"},
    "surkhandarya": {"uz": "Surxondaryo", "en": "Surkhandarya", "ru": "Сурхандарья"},
    "sirdarya": {"uz": "Sirdaryo", "en": "Sirdarya", "ru": "Сырдарья"},
    "navoiy": {"uz": "Navoiy", "en": "Navoiy", "ru": "Навои"},
    "karakalpakstan": {"uz": "Qoraqalpog‘iston", "en": "Karakalpakstan", "ru": "Каракалпакстан"},
    "jizzakh": {"uz": "Jizzax", "en": "Jizzakh", "ru": "Джизак"},
}


from aiogram.types import ReplyKeyboardRemove

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def region_inline_keyboard(language="uz"):
    """Viloyat tanlash uchun inline keyboard yaratish."""
    keyboard = []

    for key, names in REGIONS.items():
        button_text = names.get(language, names["uz"])  # Tilga mos viloyat nomi
        keyboard.append([InlineKeyboardButton(text=button_text, callback_data=f"region_{key}")])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def find_region_key(selected_region: str) -> str:
    """Foydalanuvchi tanlagan region nomi uchun asosiy kalitni ('tashkent', 'samarkand' va h.k.) topish."""
    for key, names in REGIONS.items():
        if selected_region in names.values():  # `uz`, `en`, `ru` dagi qiymatlar bo‘yicha tekshiradi
            return key
    return selected_region  # Agar topilmasa, asl qiymatni qaytaradi

@dp.message(Command("setregion"))
async def ask_region(message: types.Message, state: FSMContext):
    user = get_user(telegram_id=message.from_user.id)
    language = user.get("language", "uz")

    # 📍 Viloyat tanlash tugmalarini yuborish
    sent_message = await message.answer(
        "📍 Iltimos, o'z hududingizni tanlang:",
        reply_markup=region_inline_keyboard(language)
    )

    # ✅ Xabar ID ni saqlash (keyinchalik o‘chirish uchun)
    await state.update_data(region_message_id=sent_message.message_id)


@dp.callback_query(F.data.startswith("region_"))
async def set_region(call: types.CallbackQuery, state: FSMContext):
    user = get_user(telegram_id=call.from_user.id)
    language = user.get("language", "uz")

    selected_region_key = call.data.split("_")[1]  # Masalan, "Toshkent", "Ташкент"
    selected_region_name = find_region_key(selected_region_key)

    async with aiohttp.ClientSession() as session:
        url = f"{API_URL}/api/change_user_region/"
        data = {"telegram_id": str(call.from_user.id), "region": selected_region_name}

        async with session.post(url, json=data) as response:
            if response.status == 200:
                await call.message.delete()  # Eski xabarni o‘chirish
                sent_message = await call.message.answer(f"✅ {selected_region_name} tanlandi!")

                # ✅ Xabar ID ni saqlash
                await state.update_data(region_message_id=sent_message.message_id)

                # 📌 Asosiy menyu
                await call.message.answer(
                    "📌 Asosiy menyu:",
                    reply_markup=prayer_times_buttons(language)
                )
                await state.clear()
            else:
                await call.message.answer("❌ Xatolik yuz berdi, qayta urinib ko‘ring.")

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
from aiogram.types import BufferedInputFile
import aiohttp

API_URL = "http://127.0.0.1:8000/"

# Tillar
LANGUAGES = {
    "uz": "🇺🇿 O'zbek tili",
    "en": "🇬🇧 English",
    "ru": "🇷🇺 Русский"
}

# Viloyatlar
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


# FSM states
class UserState(StatesGroup):
    selecting_language = State()
    selecting_region = State()


# 1️⃣ Til tanlash keyboard
def language_inline_keyboard():
    builder = InlineKeyboardBuilder()
    for key, value in LANGUAGES.items():
        builder.button(text=value, callback_data=f"lang_{key}")
    builder.adjust(1)  # 1 qator, har birida 1 ta tugma
    return builder.as_markup()


# 2️⃣ Viloyat tanlash keyboard
def region_inline_keyboard(language):
    builder = InlineKeyboardBuilder()
    for key, value in REGIONS.items():
        builder.button(text=value[language], callback_data=f"region_{key}")
    builder.adjust(2)  # 2 ta tugma har bir qator
    return builder.as_markup()


# /start komandasi - Birinchi navbatda tilni so‘raydi
@dp.message(CommandStart())
async def start_chat(message: types.Message, state: FSMContext):
    user = get_user(telegram_id=message.from_user.id)

    if user == 'Not Found':
        create_user(name=message.from_user.full_name, telegram_id=message.from_user.id)
        await message.answer("🌍 Tilni tanlang | Choose a language | Выберите язык:",
                             reply_markup=language_inline_keyboard())
        await state.set_state(UserState.selecting_language)
    else:
        language = user.get('language', 'uz')
        region = user.get('region', None)

        if not region:
            await message.answer("📍 Iltimos, o'z hududingizni tanlang:", reply_markup=region_inline_keyboard(language))
            await state.set_state(UserState.selecting_region)
        else:
            await message.answer("✅ Bot sizning xizmatingizda!")
            await message.answer(
                "📌 Asosiy menyu:",
                reply_markup=prayer_times_buttons(language)
            )


# Til tanlash
@dp.callback_query(F.data.startswith("lang_"))
async def set_language(call: types.CallbackQuery, state: FSMContext):
    selected_lang = call.data.split("_")[1]

    # Tilni bazaga yozish
    change_user_language(telegram_id=call.from_user.id, language=selected_lang)

    await call.message.answer(f"✅ Til o'zgartirildi: {LANGUAGES[selected_lang]}")
    await asyncio.sleep(1)

    # Viloyat tanlashga o'tish
    await call.message.answer("📍 Iltimos, hududingizni tanlang:", reply_markup=region_inline_keyboard(selected_lang))
    await state.set_state(UserState.selecting_region)
    await call.message.delete()


# Viloyat tanlash
@dp.callback_query(F.data.startswith("region_"))
async def set_region(call: types.CallbackQuery, state: FSMContext):
    user = get_user(telegram_id=call.from_user.id)
    language = user.get("language", "uz")

    selected_region_key = call.data.split("_")[1]
    selected_region_name = REGIONS.get(selected_region_key, {}).get(language, "Noma'lum")

    # Django API-ga hududni saqlash
    async with aiohttp.ClientSession() as session:
        url = f"{API_URL}/api/change_user_region/"
        data = {"telegram_id": str(call.from_user.id), "region": selected_region_name}

        async with session.post(url, json=data) as response:
            if response.status == 200:
                await call.message.answer(f"✅ {selected_region_name} tanlandi!")
                await call.message.answer(
                    "📌 Asosiy menyu:",
                    reply_markup=prayer_times_buttons(language)
                )
                await state.clear()
            else:
                await call.message.answer("❌ Xatolik yuz berdi, qayta urinib ko‘ring.")

    await call.message.delete()  # Viloyat tanlash tugmalarini olib tashlash


@dp.callback_query(F.data == "dua")
async def send_dua(call: types.CallbackQuery):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/api/get_dua/") as response:
            if response.status == 200:
                data = await response.json()
                base64_image = data.get("image")
                caption = data.get("caption")

                if base64_image and caption:
                    # Decode Base64 image
                    image_bytes = base64.b64decode(base64_image)
                    photo = BufferedInputFile(image_bytes, filename="dua.jpg")

                    # Send photo to user
                    await call.message.answer_photo(photo=photo, caption=caption,reply_markup=prayer_times_buttons())
                else:
                    await call.message.answer("❌ Dua topilmadi.")
            else:
                await call.message.answer("❌ Xatolik yuz berdi. Keyinroq urinib ko'ring.")

@dp.callback_query(F.data == "ortga")
async def send_dua(call: types.CallbackQuery):
    await call.message.answer("Bosh menu ",reply_markup=prayer_times_buttons())



async def get_ramadan_time(call: types.CallbackQuery, day: str):
    user_id = call.from_user.id
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/api/get_ramadan_time/{user_id}/{day}/") as response:
            if response.status == 200:
                data = await response.json()
                image_bytes = base64.b64decode(data["image"])
                photo = BufferedInputFile(image_bytes, filename="ramadan.jpg")

                caption = f"📅 {day.capitalize()}'s Ramadan Time:\n"
                caption += f"🌙 Suhoor: {data['suhoor_time']}\n"
                caption += f"🌞 Iftar: {data['iftar_time']}\n\n"
                caption += data["caption"]

                await call.message.answer_photo(photo=photo, caption=caption)
            else:
                await call.message.answer("❌ Ramadan time not found for your region.")

@dp.callback_query(F.data == "today_time")
async def send_today_time(call: types.CallbackQuery):
    await get_ramadan_time(call, "today")

@dp.callback_query(F.data == "tomorrow_time")
async def send_tomorrow_time(call: types.CallbackQuery):
    await get_ramadan_time(call, "tomorrow")

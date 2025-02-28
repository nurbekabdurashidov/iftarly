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


def get_back_button_text(language):
    back_texts = {
        "uz": "🔙 Orqaga",
        "en": "🔙 Back",
        "ru": "🔙 Назад"
    }
    return back_texts.get(language, back_texts["uz"])

# Viloyat tanlash
def find_region_key(selected_region: str) -> str:
    """Foydalanuvchi tanlagan region nomi uchun asosiy kalitni ('tashkent', 'samarkand' va h.k.) topish."""
    for key, names in REGIONS.items():
        if selected_region in names.values():  # `uz`, `en`, `ru` dagi qiymatlar bo‘yicha tekshiradi
            return key
    return selected_region

@dp.callback_query(F.data.startswith("region_"))
async def set_region(call: types.CallbackQuery, state: FSMContext):
    user = get_user(telegram_id=call.from_user.id)
    language = user.get("language", "uz")

    selected_region_key = call.data.split("_")[1]  # Masalan, "Toshkent", "Ташкент"
    selected_region_name = find_region_key(selected_region_key)

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
    user_id = call.from_user.id
    user = get_user(telegram_id=user_id)
    language = user.get("language", "uz")

    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/api/get_dua/") as response:
            if response.status == 200:
                data = await response.json()
                base64_image = data.get("image")
                caption = data.get("caption", "📜 Dua")

                if base64_image:
                    try:
                        # Base64 ni dekodlash
                        image_bytes = base64.b64decode(base64_image)
                        photo = BufferedInputFile(image_bytes, filename="dua.jpg")

                        # "Orqaga" tugmasi
                        keyboard = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text=get_back_button_text(language), callback_data="back_menu")]
                        ])

                        # Rasmni yuborish
                        await call.message.answer_photo(photo=photo, caption=caption, reply_markup=keyboard)

                    except Exception as e:
                        await call.message.answer(f"❌ Rasmni yuklashda xatolik: {str(e)}")
                else:
                    await call.message.answer("❌ Dua rasmi topilmadi.")
            else:
                await call.message.answer("❌ Xatolik yuz berdi. Keyinroq urinib ko'ring.")





async def get_ramadan_time(call: types.CallbackQuery, day: str):
    user_id = call.from_user.id
    user = get_user(telegram_id=user_id)
    language = user.get("language", "uz")
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
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text=get_back_button_text(language), callback_data="back_menu")]
                ])
                await call.message.answer_photo(photo=photo, caption=caption,reply_markup=keyboard)
            else:
                await call.message.answer("❌ Ramadan time not found for your region.")

@dp.callback_query(F.data == "today_time")
async def send_today_time(call: types.CallbackQuery):
    await get_ramadan_time(call, "today")

@dp.callback_query(F.data == "tomorrow_time")
async def send_tomorrow_time(call: types.CallbackQuery):
    await get_ramadan_time(call, "tomorrow")

from aiogram.types import (
    BufferedInputFile,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InputMediaPhoto
)
@dp.callback_query(F.data == "monthly_times")
async def sendee(call: types.CallbackQuery):
    user_id = call.message.chat.id
    user = get_user(telegram_id=user_id)
    language = user.get("language", "uz")

    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/api/get_monthly_times/") as response:
            if response.status != 200:
                await call.message.answer("❌ Ma'lumotlarni yuklab bo‘lmadi.")
                return

            data = await response.json()

    if "error" in data:
        await call.message.answer(f"❌ Xatolik: {data['error']}")
        return

    try:
        # ✅ Decode Base64 Image
        image_bytes = base64.b64decode(data["image"])
        photo = BufferedInputFile(image_bytes, filename="ramadan.jpg")

        # ✅ Send Photo
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_back_button_text(language), callback_data="back_menu")]
        ])

        await call.message.delete()

        # ✅ Yangi rasm yuborish
        await call.message.answer_photo(photo=photo, caption=data["caption"], parse_mode="Markdown",
                                        reply_markup=keyboard)

    except Exception as e:
        await call.message.answer("❌ Rasmni jo‘natishda xatolik yuz berdi.")
        print(f"❌ Error: {e}")


@dp.callback_query(F.data == "donate")
async def send_support_message(call: types.CallbackQuery):
    user_id = call.from_user.id

    # Fetch user data from the database
    user = get_user(telegram_id=user_id)
    language = user.get("language", "uz")  # Default to Uzbek if no language is found

    # Define messages in different languages
    messages = {
        "uz": (
            "🤝 **Savobli Ishga Hissa Qo‘shing**\n\n"
            "❗️Sizning ehsoningiz bevosita xayriya loyihalariga yo‘naltiriladi. "
            "Biz ushbu mablag‘larni o‘zimiz uchun yig‘maymiz.\n\n"
            "💳 **Karta Raqami:** `4198 1300 4821 3341`\n"
            "👤 **Karta Egasi:** Turdiyeva Aziza"
        ),
        "en": (
            "🤝 **Support a Good Cause**\n\n"
            "❗️Your donation will go directly to charity projects. "
            "We do not collect funds for ourselves.\n\n"
            "💳 **Card Number:** `4198 1300 4821 3341`\n"
            "👤 **Cardholder Name:** Turdiyeva Aziza"
        ),
        "ru": (
            "🤝 **Поддержите Благотворительность**\n\n"
            "❗️Ваше пожертвование пойдет напрямую на благотворительные проекты. "
            "Мы не собираем средства для себя.\n\n"
            "💳 **Номер Карты:** `4198 1300 4821 3341`\n"
            "👤 **Имя Владельца Карты:** Турдиева Азиза"
        ),
    }

    # Get the appropriate message (default to Uzbek if language not found)
    message_text = messages.get(language, messages["uz"])
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_back_button_text(language), callback_data="back_menu")]
    ])
    # Send the message
    await call.message.edit_text(message_text, parse_mode="Markdown",reply_markup=keyboard)

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Back button text for different languages
 # Default to Uzbek


@dp.callback_query(F.data == "settings")
async def send_settings_message(call: types.CallbackQuery):
    user_id = call.from_user.id

    # Fetch user data from the database
    user = get_user(telegram_id=user_id)
    language = user.get("language", "uz")  # Default to Uzbek if not found

    # Define messages in different languages
    messages = {
        "uz": (
            "⚙️ **Sozlamalar**\n\n"
            "🔄 **Botni qayta ishga tushurish:** /start\n"
            "🌍 **Tilni o‘zgartirish:** /set_language\n"
            "📍 **Hududni o‘zgartirish:** /set_region"
        ),
        "en": (
            "⚙️ **Settings**\n\n"
            "🔄 **Restart Bot:** /start\n"
            "🌍 **Change Language:** /set_language\n"
            "📍 **Change Region:** /set_region"
        ),
        "ru": (
            "⚙️ **Настройки**\n\n"
            "🔄 **Перезапустить бота:** /start\n"
            "🌍 **Изменить язык:** /set_language\n"
            "📍 **Изменить регион:** /set_region"
        ),
    }

    # Get the appropriate message (default to Uzbek if language not found)
    message_text = messages.get(language, messages["uz"])

    # Create inline keyboard with "Orqaga" (Back) button
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_back_button_text(language), callback_data="back_menu")]
    ])

    # Send the message with the back button
    await call.message.edit_text(message_text, parse_mode="Markdown", reply_markup=keyboard)


@dp.callback_query(F.data == "back_menu")
async def go_back_menu(call: types.CallbackQuery):
    user_id = call.from_user.id
    user = get_user(telegram_id=user_id)
    language = user.get("language", "uz")

    # Define back message translations
    back_messages = {
        "uz": "🔙 Asosiy Menu",
        "en": "🔙 Main Menu",
        "ru": "🔙 Главное меню",
    }

    # Get the correct message based on user language
    back_text = back_messages.get(language, back_messages["uz"])

    # Send "Orqaga" confirmation

    await call.message.delete()

    # Asosiy menyuga qaytish
    await call.message.answer("📋 Tanlang:", parse_mode="Markdown", reply_markup=prayer_times_buttons(language))

import asyncio

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
    await call.message.delete()
    await asyncio.sleep(5)
    await data.delete()

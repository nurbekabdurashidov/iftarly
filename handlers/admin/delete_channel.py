from loader import dp,bot
from aiogram import types,F
from filters import *
from states.mystate import AddChannelState
from aiogram.fsm.context import FSMContext
from data.config import BOT_ID
from aiogram.utils.keyboard import InlineKeyboardBuilder,InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData
from api import get_all_channels,delete_channel
from keyboards.default.buttons import back_button,admin_button
class CheckDeleteChannel(CallbackData,prefix='ikb4'):
    id:str
@dp.message(F.text=="🗣 Kanallar",IsChatAdmin(),IsPrivate())
async def start_add_channel(message:types.Message,state:FSMContext):
    CHANNELS = get_all_channels()
    btn = InlineKeyboardBuilder()
    for channel  in CHANNELS:
        try:
            kanal = await bot.get_chat(chat_id=channel['channel_id'])
            title = kanal.title
            btn.button(text=f"{title} | ❌", callback_data=CheckDeleteChannel(id=channel['channel_id']))
            btn.adjust(1)
        except Exception as e:
            pass
    await message.answer("O'chirmoqchi bo'lgan kanaliz ustiga bosing!", reply_markup=btn.as_markup())
@dp.callback_query(CheckDeleteChannel.filter(),IsChatAdmin())
async def get(call:types.CallbackQuery,callback_data:CheckDeleteChannel,state:FSMContext):
    channel_id = callback_data.id
    try:
        delete_channel(channel_id=channel_id)
    except:
        pass
    await call.answer("Kanal o'chirildi!",show_alert=True)
    await call.message.answer("🔝 Admin panel!", reply_markup=admin_button())
    await call.message.delete()




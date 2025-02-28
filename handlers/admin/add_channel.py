from loader import dp,bot
from aiogram import types,F
from filters import IsChatAdmin,IsPrivate
from states.mystate import AddChannelState
from aiogram.fsm.context import FSMContext
from data.config import BOT_ID
from aiogram.utils.keyboard import InlineKeyboardBuilder,InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData
from api import add_channel
from keyboards.default.buttons import back_button,admin_button
class CheckAddChannel(CallbackData,prefix='ikb2'):
    id:str
    name:str
    subscribers:str
@dp.message(F.text=="🗣 Kanal qo'shish",IsChatAdmin(),IsPrivate())
async def start_add_channel(message:types.Message,state:FSMContext):
    await message.answer("Kanal ID sini tashang!",reply_markup=back_button())
    await state.set_state(AddChannelState.id)
@dp.message(F.text,IsChatAdmin(),AddChannelState.id,IsPrivate())
async def test(message:types.Message,state:FSMContext):
    if message.text=='◀️ Orqaga':
        await message.answer("🔝 Admin panel!", reply_markup=admin_button())
        await state.clear()
    else:
        try:
            channel = await bot.get_chat(chat_id=message.text)
            if channel.type == 'channel':
                link = await channel.export_invite_link()
                title = channel.title
                try:
                    subscribers = await bot.get_chat_member_count(chat_id=message.text)
                    subscribers = str(subscribers)
                except Exception as e:
                    print(e)
                    subscribers='0'
                btn = InlineKeyboardBuilder()
                btn.add(InlineKeyboardButton(text=title, url=link))
                btn.button(text="Kanalni qo'shish va tasdiqlash", callback_data=CheckAddChannel(id=message.text,name=title,subscribers=subscribers))
                btn.adjust(1, 1)
                await message.answer("Kanalni tasdiqlaysizmi?", reply_markup=btn.as_markup())
                await state.set_state(AddChannelState.check)
            else:
                await message.answer("Kanal ID sini tashang", reply_markup=back_button())
                await state.set_state(AddChannelState.id)
        except Exception as e:
            print(e)
            await message.answer("Iltimos botni kanalga admin qiling!", reply_markup=back_button())
            await state.set_state(AddChannelState.id)
@dp.callback_query(CheckAddChannel.filter(),IsChatAdmin(),AddChannelState.check)
async def get(call:types.CallbackQuery,callback_data:CheckAddChannel,state:FSMContext):
    await call.answer("Kanal qo'shildi",show_alert=True)
    channel_id = callback_data.id
    channel_name = callback_data.name
    subscribers = callback_data.subscribers
    add_channel(channel_id=channel_id,channel_name=channel_name,channel_members_count=subscribers)
    await call.message.answer("🔝 Admin panel!", reply_markup=admin_button())
    await call.message.delete()
    await state.clear()




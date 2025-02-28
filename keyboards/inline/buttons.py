from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
class Format(CallbackData,prefix='ikb0000'):
    choose:str
class LanguageCallback(CallbackData,prefix='ikb0001'):
    language:str
def text_format(choose=None):
    choose = 'TEXT' if choose==None else choose
    btn  = InlineKeyboardBuilder()
    btn.button(text=f"Markup format: {choose}",callback_data=Format(choose=choose))
    return btn.as_markup()
def language_button():
    btn = InlineKeyboardBuilder()
    btn.button(text="🇺🇿 O'zbek tili",callback_data=LanguageCallback(language='uz'))
    btn.button(text="🇬🇧 English",callback_data=LanguageCallback(language='en'))
    btn.button(text="🇷🇺 Russian", callback_data=LanguageCallback(language='ru'))
    btn.adjust(1)
    return btn.as_markup()
from aiogram.utils.keyboard import ReplyKeyboardBuilder,KeyboardButton
def admin_button():
    button = ReplyKeyboardBuilder()
    button.row(
        KeyboardButton(text="🗣 Reklama yuborish"),
        KeyboardButton(text="📊 Obunachilar soni"),

    )
    button.row(KeyboardButton(text="🗣 Kanal qo'shish"),
               KeyboardButton(text="🗣 Kanallar"))
    button.adjust(2,2)
    return button.as_markup(resize_keyboard=True,one_time_keyboard=True,input_field_placeholder="Kerakli bo'limni tanlang!")
def add_type():
    button = ReplyKeyboardBuilder()
    button.row(
        KeyboardButton(text="📝 Tekst"),
        KeyboardButton(text="📸 Rasm")
    )
    button.row(
        KeyboardButton(text="🎞 Video"),
        KeyboardButton(text="⬅️ Orqaga")
    )
    button.adjust(2)
    return button.as_markup(resize_keyboard=True, one_time_keyboard=True)
def back_button():
    button = ReplyKeyboardBuilder()

    button.row(

        KeyboardButton(text="◀️ Orqaga")
    )
    button.adjust(2)
    return button.as_markup(resize_keyboard=True, one_time_keyboard=True)
def need_or_not():
    button = ReplyKeyboardBuilder()

    button.row(
        KeyboardButton(text="⏺ Bekor qilish"),
        KeyboardButton(text="🆗 Kerakmas")
    )
    button.adjust(2)
    return button.as_markup(resize_keyboard=True, one_time_keyboard=True)
def send():
    button = ReplyKeyboardBuilder()

    button.row(
        KeyboardButton(text="⏺ Bekor qilish"),
        KeyboardButton(text="📤 Yuborish")
    )
    button.adjust(2)
    return button.as_markup(resize_keyboard=True, one_time_keyboard=True)


from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

def prayer_times_buttons(language="uz"):
    button = InlineKeyboardBuilder()

    # Tugmalarni tarjima qilish
    translations = {
        "uz": {
            "monthly": "📅 Oylik vaqtlar",
            "today": "🌞 Bugungi vaqt",
            "tomorrow": "🌙 Ertangi vaqt",
            "dua": "🙏 Duo",
            "settings": "⚙ Sozlamalar",
            "donate": "❤️ Xayriya"
        },
        "en": {
            "monthly": "📅 Monthly Times",
            "today": "🌞 Today's Time",
            "tomorrow": "🌙 Tomorrow's Time",
            "dua": "🙏 Dua",
            "settings": "⚙ Settings",
            "donate": "❤️ Donate"
        },
        "ru": {
            "monthly": "📅 Ежемесячное время",
            "today": "🌞 Сегодняшнее время",
            "tomorrow": "🌙 Завтрашнее время",
            "dua": "🙏 Дуа",
            "settings": "⚙ Настройки",
            "donate": "❤️ Пожертвование"
        }
    }

    t = translations.get(language, translations["uz"])  # Default Uzbek

    # 1-qator: Oylik vaqtlar
    button.row(
        InlineKeyboardButton(text=t["monthly"], callback_data="monthly_times")
    )

    # 2-qator: Bugungi vaqt | Ertangi vaqt
    button.row(
        InlineKeyboardButton(text=t["today"], callback_data="today_time"),
        InlineKeyboardButton(text=t["tomorrow"], callback_data="tomorrow_time")
    )

    # 3-qator: Duo | Sozlamalar
    button.row(
        InlineKeyboardButton(text=t["dua"], callback_data="dua"),
        InlineKeyboardButton(text=t["settings"], callback_data="settings")
    )

    # 4-qator: Xayriya
    button.row(
        InlineKeyboardButton(text=t["donate"], callback_data="donate")
    )

    return button.as_markup()

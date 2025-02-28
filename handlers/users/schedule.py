import asyncio
import datetime
import base64
import aiohttp
import pytz
from aiogram.types import BufferedInputFile
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loader import bot

API_URL = "http://127.0.0.1:8000/"
scheduler = AsyncIOScheduler()

async def send_iftar_message(user_id, region, image_base64, caption):
    """Foydalanuvchiga iftor haqida eslatma yuborish."""
    try:
        image_bytes = base64.b64decode(image_base64)
        photo = BufferedInputFile(image_bytes, filename="ramadan.jpg")

        await bot.send_photo(
            chat_id=user_id,
            photo=photo,
            caption=f"⏳ 15 daqiqa qoldi iftor uchun ({region})!\n\n{caption}"
        )
    except Exception as e:
        print(f"Xatolik {user_id} uchun iftor eslatmasini yuborishda: {e}")

async def schedule_iftar_reminders():
    """Barcha foydalanuvchilar uchun iftor vaqtini jadvalga qo‘shish."""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/api/get_all_users/") as response:
            if response.status != 200:
                print("❌ Foydalanuvchilarni olishda xatolik")
                return

            users = await response.json()

            for user in users:
                user_id = user["telegram_id"]
                region = user["region"]

                async with session.get(f"{API_URL}/api/get_ramadan_time/{user_id}/today/") as response:
                    if response.status == 200:
                        data = await response.json()

                        # ✅ 1. Iftar vaqtini olish va tekshirish
                        try:
                            now = datetime.datetime.now(pytz.utc)  # UTC vaqt
                            iftar_time = datetime.datetime.strptime(data["iftar_time"], "%H:%M")
                            iftar_time = iftar_time.replace(
                                year=now.year, month=now.month, day=now.day, tzinfo=pytz.utc
                            )

                            # ✅ 2. 15 daqiqa oldin xabar yuborish uchun vaqtni aniqlash
                            notify_time = iftar_time - datetime.timedelta(minutes=15)

                            # ✅ 3. O‘tib ketgan vaqtni rejalashtirmaslik
                            if notify_time > now:
                                scheduler.add_job(
                                    send_iftar_message,
                                    "date",
                                    run_date=notify_time,
                                    args=[user_id, region, data["image"], data["caption"]]
                                )
                                print(f"✅ {user_id} uchun iftor eslatmasi {notify_time} ga rejalashtirildi.")
                            else:
                                print(f"⏳ {user_id} uchun iftor eslatmasi allaqachon o‘tib ketgan, qo‘shilmadi.")

                        except Exception as e:
                            print(f"❌ {user_id} uchun iftor vaqtini qayta ishlashda xatolik: {e}")

async def start_scheduler():
    """Scheduler'ni ishga tushirish va har kuni yangi eslatmalarni qo‘shish."""
    scheduler.start()
    while True:
        await schedule_iftar_reminders()  # ✅ Har kuni yangilash
        await asyncio.sleep(86400)  # 24 soat kutish

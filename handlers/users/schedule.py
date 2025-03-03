# import asyncio
# import datetime
# import base64
# import aiohttp
# from aiogram.types import BufferedInputFile
# from apscheduler.schedulers.asyncio import AsyncIOScheduler
# from loader import bot
#
# API_URL = "https://iftarly.pythonanywhere.com/"
# scheduler = AsyncIOScheduler()
#
#
# async def fetch_users():
#     """Fetch all users from API."""
#     async with aiohttp.ClientSession() as session:
#         async with session.get(f"{API_URL}/api/get_all_users/") as response:
#             if response.status != 200:
#                 print(f"❌ Failed to fetch users: {await response.text()}")
#                 return []
#             return await response.json()
#
#
# async def fetch_ramadan_time(session, user_id):
#     """Fetch Suhoor and Iftar times for a given user_id."""
#     url = f"{API_URL}/api/get_ramadan_time/{user_id}/today/"
#     try:
#         async with session.get(url) as response:
#             if response.status == 200:
#                 return await response.json()
#             else:
#                 error_text = await response.text()
#                 print(f"❌ API Error for user {user_id}: {error_text}")
#                 return None
#     except Exception as e:
#         print(f"❌ Request failed for {user_id}: {e}")
#         return None
#
#
# async def send_reminder(user_id, event, image, caption):
#     """Send a reminder message for Suhoor or Iftar."""
#     try:
#         image_bytes = base64.b64decode(image)
#         photo = BufferedInputFile(image_bytes, filename="ramadan.jpg")
#
#         event_text = "Suhoor" if event == "suhoor" else "Iftar"
#         await bot.send_photo(
#             chat_id=user_id,
#             photo=photo,
#             caption=f"⏳ 15 minutes left for {event_text}!\n\n{caption}"
#         )
#         print(f"✅ Sent {event_text} reminder to {user_id}")
#
#     except Exception as e:
#         print(f"❌ Failed to send {event_text} reminder to {user_id}: {e}")
#
#
# async def send_suhoor_reminders():
#     """Send Suhoor reminders to all users."""
#     print(f"⏳ Sending Suhoor reminders at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
#     users = await fetch_users()
#
#     async with aiohttp.ClientSession() as session:
#         for user in users:
#             user_id = user["telegram_id"]
#             data = await fetch_ramadan_time(session, user_id)
#             if not data:
#                 continue
#
#             await send_reminder(user_id, "suhoor", data["image"], data["caption"])
#
#
# async def send_iftar_reminders():
#     """Send Iftar reminders to all users."""
#     print(f"⏳ Sending Iftar reminders at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
#     users = await fetch_users()
#
#     async with aiohttp.ClientSession() as session:
#         for user in users:
#             user_id = user["telegram_id"]
#             data = await fetch_ramadan_time(session, user_id)
#             if not data:
#                 continue
#
#             await send_reminder(user_id, "iftar", data["image"], data["caption"])
#
#
# async def schedule_jobs():
#     """Schedule Suhoor and Iftar reminders."""
#     users = await fetch_users()
#     if not users:
#         print("❌ No users found. Jobs not scheduled.")
#         return
#
#     async with aiohttp.ClientSession() as session:
#         first_user = users[0]
#         data = await fetch_ramadan_time(session, first_user["telegram_id"])
#         if not data:
#             print("❌ No time data found for scheduling.")
#             return
#
#         try:
#             suhoor_time = datetime.datetime.strptime(data["suhoor_time"], "%H:%M").time()
#             iftar_time = datetime.datetime.strptime(data["iftar_time"], "%H:%M").time()
#         except ValueError:
#             print("❌ Invalid time format in API response.")
#             return
#
#     # ✅ 15 minutes before Suhoor
#     suhoor_reminder_time = (datetime.datetime.combine(datetime.date.today(), suhoor_time) -
#                             datetime.timedelta(minutes=15)).time()
#
#     # ✅ 15 minutes before Iftar
#     iftar_reminder_time = (datetime.datetime.combine(datetime.date.today(), iftar_time) -
#                            datetime.timedelta(minutes=15)).time()
#
#     scheduler.add_job(send_suhoor_reminders, "cron", hour=suhoor_reminder_time.hour,
#                       minute=suhoor_reminder_time.minute, id="suhoor_reminder")
#
#     scheduler.add_job(send_iftar_reminders, "cron", hour=iftar_reminder_time.hour,
#                       minute=iftar_reminder_time.minute, id="iftar_reminder")
#
#     print("✅ Scheduled Suhoor and Iftar reminders!")
#
#
# async def start_scheduler():
#     """Start the scheduler and schedule jobs dynamically."""
#     await schedule_jobs()
#     scheduler.start()
#     print("✅ Scheduler started successfully!")
#     print(f"📌 Scheduled Jobs: {scheduler.get_jobs()}")

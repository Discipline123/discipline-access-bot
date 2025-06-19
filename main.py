import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

BOT_TOKEN = os.getenv("BOT_TOKEN")
channel = os.getenv("CHANNEL_ID")
if channel is None:
    raise Exception("CHANNEL_ID not set")

CHANNEL_ID = int(channel)
TRIAL_DURATION = 3600  # 1 час

user_entry_times = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in user_entry_times:
        await update.message.reply_text("Ты уже получил доступ 👌")
        return

    user_entry_times[user_id] = datetime.now()
    button = InlineKeyboardButton("Перейти в канал", url="https://t.me/+m7n_F5gM1Zk1ZDNi")
    reply_markup = InlineKeyboardMarkup([[button]])
    await update.message.reply_text("Ты получил доступ на 1 час 👇", reply_markup=reply_markup)

async def check_access(context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now()
    for user_id, entry_time in list(user_entry_times.items()):
        if (now - entry_time).total_seconds() > TRIAL_DURATION:
            try:
                await context.bot.ban_chat_member(CHANNEL_ID, user_id)
                await context.bot.unban_chat_member(CHANNEL_ID, user_id)
                del user_entry_times[user_id]
            except Exception as e:
                print(f"Ошибка при удалении доступа {user_id}: {e}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.job_queue.run_repeating(check_access, interval=60, first=10)
    print("Бот запущен")
    app.run_polling()

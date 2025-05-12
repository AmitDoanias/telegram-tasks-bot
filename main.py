import logging
import time
import schedule
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, CallbackQueryHandler, filters

TOKEN = "7782428550:AAFLxweTZgGk97m3VGEridLvbLMZ8uFqR0Y"
USER_ID = 529035487

task_list = []

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def main_menu():
    keyboard = [["הוסף משימה", "הצג רשימה"], ["משימה הושלמה"]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="ברוך הבא עמית! השתמש בכפתורים למטה או שלח פקודה ידנית.",
        reply_markup=main_menu()
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text

    if message.startswith("הוסף:") or message == "הוסף משימה":
        if message.startswith("הוסף:"):
            task_item = message.replace("הוסף:", "").strip()
            task_list.append(task_item)
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f'המשימה "{task_item}" נוספה ✅')
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="כתוב את המשימה בפורמט: הוסף: [משימה]")
    elif message == "הצג רשימה" or message == "רשימה":
        if task_list:
            response = "📋 רשימת המשימות שלך:\n" + "\n".join([f"• {t}" for t in task_list])
        else:
            response = "אין כרגע משימות ברשימה 🎉"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response)
    elif message == "משימה הושלמה":
        if not task_list:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="אין משימות לסיים ✅")
            return
        buttons = [[InlineKeyboardButton(text=task, callback_data=f"done|{task}")] for task in task_list]
        reply_markup = InlineKeyboardMarkup(buttons)
        await context.bot.send_message(chat_id=update.effective_chat.id, text="בחר את המשימה שהושלמה:", reply_markup=reply_markup)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("done|"):
        task_done = data.split("|")[1]
        if task_done in task_list:
            task_list.remove(task_done)
            await context.bot.send_message(chat_id=USER_ID, text=f'המשימה "{task_done}" סומנה כהושלמה והוסרה ✅')
        else:
            await context.bot.send_message(chat_id=USER_ID, text="המשימה כבר הוסרה או לא נמצאה.")

async def send_evening_reminder(context: ContextTypes.DEFAULT_TYPE):
    if task_list:
        tasks = "\n".join([f"• {t}" for t in task_list])
        await context.bot.send_message(chat_id=USER_ID, text=f"🌙 ערב טוב עמית! הנה המשימות למחר:\n{tasks}")

async def send_morning_reminder(context: ContextTypes.DEFAULT_TYPE):
    if task_list:
        tasks = "\n".join([f"• {t}" for t in task_list])
        await context.bot.send_message(chat_id=USER_ID, text=f"☀️ בוקר טוב עמית! המשימות שלך להיום:\n{tasks}")

def run_scheduler(application):
    schedule.every().day.at("21:00").do(lambda: application.create_task(send_evening_reminder(application.bot)))
    schedule.every().day.at("08:45").do(lambda: application.create_task(send_morning_reminder(application.bot)))
    while True:
        schedule.run_pending()
        time.sleep(60)

def main():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(handle_callback))

    import threading
    threading.Thread(target=run_scheduler, args=(application,), daemon=True).start()
    application.run_polling()

if __name__ == "__main__":
    main()

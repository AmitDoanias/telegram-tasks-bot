
import logging
import time
import schedule
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

TOKEN = "7782428550:AAFLxweTZgGk97m3VGEridLvbLMZ8uFqR0Y"
USER_ID = 529035487

task_list = []

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="היי עמית! שלח לי משימה עם המילה 'הוסף:'")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text
    if message.startswith("הוסף:"):
        task_item = message.replace("הוסף:", "").strip()
        task_list.append(task_item)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f'המשימה "{task_item}" נוספה לרשימה ✅')
    elif message.startswith("סיימתי:"):
        done_task = message.replace("סיימתי:", "").strip()
        if done_task in task_list:
            task_list.remove(done_task)
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f'המשימה "{done_task}" הוסרה ✅')
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="המשימה לא נמצאה 🤔")
    elif message == "רשימה":
        if task_list:
            response = "📋 רשימת המשימות שלך:
" + "
".join([f"• {t}" for t in task_list])
        else:
            response = "אין כרגע משימות ברשימה 🎉"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response)

async def send_evening_reminder(context: ContextTypes.DEFAULT_TYPE):
    if task_list:
        tasks = "
".join([f"• {t}" for t in task_list])
        await context.bot.send_message(chat_id=USER_ID, text=f"🌙 ערב טוב עמית! הנה המשימות למחר:
{tasks}")

async def send_morning_reminder(context: ContextTypes.DEFAULT_TYPE):
    if task_list:
        tasks = "
".join([f"• {t}" for t in task_list])
        await context.bot.send_message(chat_id=USER_ID, text=f"☀️ בוקר טוב עמית! המשימות שלך להיום:
{tasks}")

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

    import threading
    threading.Thread(target=run_scheduler, args=(application,), daemon=True).start()
    application.run_polling()

if __name__ == "__main__":
    main()

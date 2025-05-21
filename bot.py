from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
    CommandHandler,
)
import os

ASK_TYPE, ASK_PROJECT = range(2)
temp_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Просто перешли сообщение, и я помогу его сохранить.")

async def handle_forward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if message.forward_from or message.forward_from_chat:
        text = message.text or message.caption or "[нет текста]"
        user_id = update.effective_user.id
        temp_data[user_id] = {"text": text}
        keyboard = [["Задача", "Заметка"]]
        await update.message.reply_text(
            "Что это — задача или заметка?",
            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True),
        )
        return ASK_TYPE
    else:
        await update.message.reply_text("Пожалуйста, перешли сообщение.")
        return ConversationHandler.END

async def handle_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    msg_type = update.message.text.lower()
    if msg_type in ["задача", "заметка"]:
        temp_data[user_id]["type"] = msg_type
        await update.message.reply_text("К какому проекту это относится?")
        return ASK_PROJECT
    else:
        await update.message.reply_text("Выбери 'Задача' или 'Заметка'.")
        return ASK_TYPE

async def handle_project(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    project = update.message.text
    entry = temp_data.pop(user_id, None)
    if entry:
        entry["project"] = project
        print(f"[НОВАЯ ЗАПИСЬ] {entry}")
        await update.message.reply_text("Готово! Я сохранил информацию.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отменено.")
    return ConversationHandler.END

def main():
    TOKEN = os.environ["BOT_TOKEN"]
    app = ApplicationBuilder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[MessageHandler(filters.FORWARDED, handle_forward)],
        states={
            ASK_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_type)],
            ASK_PROJECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_project)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv)

    app.run_polling()

if __name__ == "__main__":
    main()

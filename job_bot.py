from telegram import (
    Update,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
import datetime
import os
import json

TOKEN = os.environ.get("TOKEN")
BOT_HOUR = int(os.environ.get("BOT_HOUR", 13))
BOT_MIN = int(os.environ.get("BOT_MIN", 0))

DATA_FILE = "user_data.json"


# ====== Работа с файлами ======

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}  # пустой словарь для связок


def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(user_data, f, indent=2)


user_data = load_data()


# ====== Команды ======

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    if chat_id not in user_data:
        user_data[chat_id] = {"friend_chat_id": None}
        save_data()
    await update.message.reply_text(
        "Bot activated 🎀. Установи подругу командой: /setfriend <chat_id>"
    )


async def set_friend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)

    if not context.args:
        await update.message.reply_text(
            "Используй так: /setfriend <chat_id>. "
            "Узнать chat_id можно через бота @RawDataBot."
        )
        return

    friend_chat_id = context.args[0]

    if not friend_chat_id.isdigit():
        await update.message.reply_text("chat_id должен быть числом!")
        return

    user_data[chat_id]["friend_chat_id"] = friend_chat_id
    save_data()
    await update.message.reply_text(
        f"Теперь твоя подруга = {friend_chat_id} 🎀"
    )


async def whoisfriend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)

    if chat_id not in user_data:
        await update.message.reply_text("Ты ещё не зарегистрирован. Напиши /start.")
        return

    friend_chat_id = user_data[chat_id].get("friend_chat_id")
    if friend_chat_id:
        await update.message.reply_text(
            f"У тебя сохранён friend_chat_id = {friend_chat_id} 🎀"
        )
    else:
        await update.message.reply_text("У тебя пока не задан друг. Напиши /setfriend <chat_id>.")


# ====== Ежедневный вопрос ======

async def daily_question(context: ContextTypes.DEFAULT_TYPE):
    app = context.application
    for main_user, info in user_data.items():
        keyboard = ReplyKeyboardMarkup([["Yes", "No"]], resize_keyboard=True)

        if os.path.exists("image.jpg"):
            with open("image.jpg", "rb") as photo:
                await app.bot.send_photo(
                    chat_id=int(main_user),
                    photo=photo,
                    caption="Have you applied for 40 jobs today, girl? 🎀",
                    reply_markup=keyboard
                )
        else:
            await app.bot.send_message(
                chat_id=int(main_user),
                text="Have you applied for 40 jobs today, girl? 🎀",
                reply_markup=keyboard
            )


# ====== Ответы ======

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    text = update.message.text.strip().lower()

    if chat_id not in user_data:
        return

    friend_chat_id = user_data[chat_id].get("friend_chat_id")

    if text == "yes":
        if os.path.exists("success.jpg"):
            with open("success.jpg", "rb") as photo:
                await update.message.reply_photo(
                    photo=photo,
                    caption="you go girl! 1 step away from poverty 🎀",
                    reply_markup=ReplyKeyboardRemove()
                )
        else:
            await update.message.reply_text(
                "you go girl! 1 step away from poverty 🎀",
                reply_markup=ReplyKeyboardRemove()
            )

        if friend_chat_id:
            await context.bot.send_message(
                chat_id=int(friend_chat_id),
                text="She's doing fine! Your friend replied for 40 jobs, maybe you will go to Bali next year 😉"
            )

    elif text == "no":
        if os.path.exists("cringe.jpg"):
            with open("cringe.jpg", "rb") as photo:
                await update.message.reply_photo(
                    photo=photo,
                    caption="you ARE cringe for not trying, you will die out of poverty",
                    reply_markup=ReplyKeyboardRemove()
                )
        else:
            await update.message.reply_text(
                "you ARE cringe for not trying, you will die out of poverty",
                reply_markup=ReplyKeyboardRemove()
            )

        if friend_chat_id:
            await context.bot.send_message(
                chat_id=int(friend_chat_id),
                text="make her not die poor! pretty please 🥹"
            )


# ====== Запуск ======

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setfriend", set_friend))
    app.add_handler(CommandHandler("whoisfriend", whoisfriend))
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, handle_answer))

    app.job_queue.run_daily(
        daily_question,
        time=datetime.time(hour=BOT_HOUR, minute=BOT_MIN)
    )

    app.run_polling()


if __name__ == "__main__":
    main()

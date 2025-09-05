from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import datetime
import asyncio

TOKEN = '8410155059:AAGunUedbT0VdrynbO7o-kIwj_p4fzlOQ-s'

user_data = {
    "main_user": None,
    "friend_username": None
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data["main_user"] = update.effective_chat.id
    await update.message.reply_text("Bot activated, hopefully you'll find a job with decent salary, girl")


async def set_friend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Set your accountability partner with: /setfriend @username")
        return
    friend_username = context.args[0]
    if not friend_username.startswith("@"):
        await update.message.reply_text("You need to set your friend formated like: /setfriend @bestie")
        return

    user_data["friend_username"] = friend_username
    await update.message.reply_text(f"This friend will be updated: {friend_username}")


async def daily_question(context: ContextTypes.DEFAULT_TYPE):
    app = context.application
    if user_data["main_user"] is not None:
        keyboard = ReplyKeyboardMarkup([["Yes", "No"]], resize_keyboard=True)
        with open("image.jpg", "rb") as photo:
            await app.bot.send_photo(
                chat_id=user_data["main_user"],
                photo=photo,
                caption="Have you applied for 40 jobs today, girl? 🎀",
                reply_markup=keyboard
            )


async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    if user_data["main_user"] != update.effective_chat.id:
        return

    friend_username = user_data["friend_username"]

    if "yes" in text:
        with open("success.jpg", "rb") as photo:
            await update.message.reply_photo(
                photo=photo,
                caption="you go girl! 1 step away from poverty 🎀",
                reply_markup=ReplyKeyboardRemove()
            )
        if friend_username is not None:
            await context.bot.send_message(friend_username, "She's doing fine! Your friend replied for 40 jobs, maybe you will go to Bali next year 😉")

    elif "no" in text:
        with open("cringe.jpg", "rb") as photo:
            await update.message.reply_photo(
                photo=photo,
                caption="you ARE cringe for not trying, you will die out of poverty",
                reply_markup=ReplyKeyboardRemove()
            )
        if friend_username is not None:
            await context.bot.send_message(friend_username, "make her not die poor! pretty please 🥹")


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setfriend", set_friend))
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, handle_answer))

    app.job_queue.run_daily(
        daily_question, time=datetime.time(hour=2, minute=30))
    app.run_polling()


if __name__ == "__main__":
    main()

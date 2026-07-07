import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# ذخیره وضعیت پاسخ‌دهی مدیر
replying_to = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "پیامت به صورت ناشناس برام ارسال میشه"
    )


async def receive_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user

    # جلوگیری از ارسال پیام خود مدیر به خودش
    if user.id == ADMIN_ID:
        return

    # ارسال پیام کاربر برای مدیر
    keyboard = [
        [
            InlineKeyboardButton(
                "پیامت رو دیدم",
                callback_data=f"seen_{user.id}"
            ),
            InlineKeyboardButton(
                "پاسخ",
                callback_data=f"reply_{user.id}"
            )
        ]
    ]

    await context.bot.copy_message(
        chat_id=ADMIN_ID,
        from_chat_id=update.message.chat_id,
        message_id=update.message.message_id,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    await update.message.reply_text(
        "پیامت ارسال شد"
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data.startswith("seen_"):
        user_id = int(data.split("_")[1])

        await context.bot.send_message(
            chat_id=user_id,
            text="پیامت رو دیدم"
        )

    elif data.startswith("reply_"):
        user_id = int(data.split("_")[1])

        replying_to[ADMIN_ID] = user_id

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text="پاسخ خود را ارسال کنید:"
        )


async def admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat_id != ADMIN_ID:
        return

    if ADMIN_ID in replying_to:
        user_id = replying_to[ADMIN_ID]

        await context.bot.copy_message(
            chat_id=user_id,
            from_chat_id=ADMIN_ID,
            message_id=update.message.message_id
        )

        del replying_to[ADMIN_ID]


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(
        CallbackQueryHandler(button_handler)
    )

    app.add_handler(
        MessageHandler(
            filters.ALL & ~filters.COMMAND,
            receive_message
        )
    )

    app.add_handler(
        MessageHandler(
            filters.ALL,
            admin_reply
        )
    )

    print("Bot started...")
    app.run_polling()


if __name__ == "__main__":
    main()

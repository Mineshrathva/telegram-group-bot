import os
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# Store how many users each person added
user_added_count = {}

# Track users who already saw warning button
warned_users = set()


# Track new members added
async def track_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.new_chat_members:
        adder = update.message.from_user.id
        for _ in update.message.new_chat_members:
            user_added_count[adder] = user_added_count.get(adder, 0) + 1


# Restrict messages until user adds 5 members
async def restrict_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user = update.message.from_user
    chat = update.message.chat

    # Admins always allowed
    admins = [admin.user.id for admin in await chat.get_administrators()]
    if user.id in admins:
        return

    added = user_added_count.get(user.id, 0)

    if added < 5:
        await update.message.delete()

        # Show warning button ONLY ONCE per user
        if user.id not in warned_users:
            warned_users.add(user.id)

            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("⚠️ Why message blocked?", callback_data="warn")]
            ])

            await context.bot.send_message(
                chat_id=chat.id,
                text="🔒 Messaging locked",
                reply_markup=keyboard
            )


# Popup alert (NO group message)
async def popup_warning(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer(
        text="🚫 You must add 5 members to start chatting.",
        show_alert=True
    )


def main():
    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN not set")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(
        MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, track_add)
    )
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, restrict_messages)
    )
    app.add_handler(
        CallbackQueryHandler(popup_warning, pattern="warn")
    )

    print("🤖 Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()

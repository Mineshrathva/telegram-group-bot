import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    ContextTypes,
    filters,
)

# Store how many users each person added
user_added_count = {}


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

    # Get admin IDs
    admins = [admin.user.id async for admin in chat.get_administrators()]
    if user.id in admins:
        return

    added = user_added_count.get(user.id, 0)

    if added < 5:
        try:
            await update.message.delete()
            await context.bot.send_message(
                chat_id=chat.id,
                text=(
                    f"🚫 {user.first_name}, add *5 members* to chat.\n"
                    f"Progress: {added}/5"
                ),
                parse_mode="Markdown",
            )
        except Exception:
            pass


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

    print("🤖 Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()

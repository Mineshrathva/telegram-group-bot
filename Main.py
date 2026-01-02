import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    ContextTypes,
    filters,
)

user_added_count = {}

async def track_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.new_chat_members:
        adder = update.message.from_user.id
        for _ in update.message.new_chat_members:
            user_added_count[adder] = user_added_count.get(adder, 0) + 1

async def restrict_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user = update.message.from_user
    chat = update.message.chat

    admins = [admin.user.id async for admin in context.bot.get_chat_administrators(chat.id)]
    if user.id in admins:
        return

    if user_added_count.get(user.id, 0) < 5:
        await update.message.delete()
        await context.bot.send_message(
            chat_id=chat.id,
            text=(
                f"🚫 {user.first_name}, add 5 members to chat.\n"
                f"Progress: {user_added_count.get(user.id, 0)}/5"
            ),
        )

async def main():
    token = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(token).build()

    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, track_add))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, restrict_messages))

    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

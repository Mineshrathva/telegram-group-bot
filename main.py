import os
import asyncio
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

user_added_count = {}
warned_users = set()


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

    admins = [a.user.id for a in await chat.get_administrators()]
    if user.id in admins:
        return

    if user_added_count.get(user.id, 0) < 5:
        await update.message.delete()

        if user.id not in warned_users:
            warned_users.add(user.id)

            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton(" ", callback_data="warn")]
            ])

            msg = await context.bot.send_message(
                chat_id=chat.id,
                text=".",
                reply_markup=keyboard
            )

            # auto delete helper message
            await asyncio.sleep(0.5)
            await msg.delete()


async def popup_warning(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer(
        text="🚫 You must add 5 members to start chatting.",
        show_alert=True
    )


def main():
    app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()

    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, track_add))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, restrict_messages))
    app.add_handler(CallbackQueryHandler(popup_warning, pattern="warn"))

    app.run_polling()


if __name__ == "__main__":
    main()

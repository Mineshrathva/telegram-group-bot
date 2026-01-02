import os
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext

user_added_count = {}

def track_add(update: Update, context: CallbackContext):
    if update.message and update.message.new_chat_members:
        adder = update.message.from_user.id
        for _ in update.message.new_chat_members:
            user_added_count[adder] = user_added_count.get(adder, 0) + 1

def restrict_messages(update: Update, context: CallbackContext):
    if not update.message or not update.message.text:
        return

    user = update.message.from_user
    chat = update.message.chat

    admins = [admin.user.id for admin in chat.get_administrators()]
    if user.id in admins:
        return

    if user_added_count.get(user.id, 0) < 5:
        try:
            update.message.delete()
            context.bot.send_message(
                chat_id=chat.id,
                text=(
                    f"🚫 {user.first_name}, add **5 members** to chat.\n"
                    f"Progress: {user_added_count.get(user.id, 0)}/5"
                ),
                parse_mode="Markdown"
            )
        except:
            pass

def main():
    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN not set")

    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, track_add))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, restrict_messages))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()

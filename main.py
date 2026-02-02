import os
from telegram import Update
from telegram.constants import ChatMemberStatus
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters


def _is_allowed_status(status: str) -> bool:
    return status in {
        ChatMemberStatus.MEMBER,
        ChatMemberStatus.ADMINISTRATOR,
        ChatMemberStatus.OWNER,
    }


async def enforce_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user is None or update.effective_chat is None:
        return

    required_chat = os.environ.get("REQUIRED_CHAT")
    if not required_chat:
        return

    user_id = update.effective_user.id
    try:
        member = await context.bot.get_chat_member(required_chat, user_id)
    except Exception:
        return

    if _is_allowed_status(member.status):
        return

    if update.message is None:
        return

    try:
        await update.message.delete()
    except Exception:
        return

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            "Чтобы писать в чате, подпишитесь на обязательный канал/чат: "
            f"{required_chat}"
        ),
        reply_to_message_id=update.message.message_id,
    )


def main() -> None:
    token = os.environ.get("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN is required")

    app = ApplicationBuilder().token(token).build()
    app.add_handler(MessageHandler(filters.ALL, enforce_subscription))
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

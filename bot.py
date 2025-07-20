import os
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler
)

from dotenv import load_dotenv

load_dotenv()

WAITING_TEXT, WAITING_VOICE = 0, 1 # состояния диалога
class SpeechAnalystBot:
    def __init__(self):
        self.user_data = {}

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user = update.message.from_user

        await update.message.reply_text(
            "👋 Привет! Я помогу тебе улучшить твои устные ответы.\n\n"
            "📝 Пожалуйста, отправь мне текстовый параграф (например, из учебника), "
            "который ты хочешь отработать."
        )

        return WAITING_TEXT

    """прерывание диалога"""
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user = update.message.from_user

        chat_id = update.effective_chat.id
        if chat_id in self.user_data:
            del self.user_data[chat_id]

        await update.message.reply_text(
            "Диалог прерван. Чтобы начать заново, отправь /start"
        )

        return ConversationHandler.END


    def run(self):
        app = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.start)],
            states={
            },
            fallbacks=[CommandHandler('cancel', self.cancel)],
        )

        app.add_handler(conv_handler)
        app.run_polling()


if __name__ == "__main__":
    bot = SpeechAnalystBot()
    bot.run()
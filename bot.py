import os
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler
)
from audio_processor import AudioProcessor
# from text_analyzer import TextAnalyzer
# from report_generator import ReportGenerator
import config
from dotenv import load_dotenv

load_dotenv()

# Состояния диалога
WAITING_TEXT, WAITING_VOICE = 0, 1


class SpeechAnalystBot:
    def __init__(self):
        self.audio_processor = AudioProcessor()

        self.user_data = {}
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO
        )

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Обработка команды /start - начало взаимодействия"""
        user = update.message.from_user
        self.logger.info("Пользователь %s начал диалог.", user.first_name)

        # Очищаем предыдущие данные
        chat_id = update.effective_chat.id
        if chat_id in self.user_data:
            del self.user_data[chat_id]

        await update.message.reply_text(
            "👋 Привет! Я помогу тебе улучшить твои устные ответы.\n\n"
            "📝 Пожалуйста, отправь мне текстовый параграф (например, из учебника), "
            "который ты хочешь отработать."
        )

        return WAITING_TEXT

    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Обработка текстового параграфа от пользователя"""
        chat_id = update.effective_chat.id
        text = update.message.text


        self.user_data[chat_id] = {"paragraph": text}
        self.logger.info("Пользователь %s отправил текст: %s", chat_id, text[:50] + "...")

        await update.message.reply_text(
            "✅ Текст получен! Теперь отправь мне голосовое сообщение "
            "с твоим устным ответом по этой теме."
        )

        return WAITING_VOICE

    async def handle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Обработка голосового сообщения"""
        chat_id = update.effective_chat.id
        self.logger.info("Пользователь %s отправил голосовое сообщение", chat_id)


        if chat_id not in self.user_data or "paragraph" not in self.user_data[chat_id]:
            await update.message.reply_text(
                "⚠️ Сначала отправь текстовый параграф командой /start!"
            )
            return WAITING_TEXT

        try:

            voice_file = await update.message.voice.get_file()
            audio_path = f"temp_{chat_id}.ogg"
            await voice_file.download_to_drive(audio_path)


            await update.message.reply_text("🔍 Обрабатываю твой ответ...")

            # Транскрибация
            user_text = self.audio_processor.transcribe_audio(audio_path)
            self.logger.info("Транскрибированный текст: %s", user_text[:100] + "...")

            # Анализ
            paragraph = self.user_data[chat_id]["paragraph"]



            # report = ReportGenerator.generate(structure, parasites)
            report = paragraph  + user_text
            await update.message.reply_text(report)


            os.remove(audio_path)
            del self.user_data[chat_id]


            await update.message.reply_text(
                "🔄 Хочешь попробовать с другим текстом? Отправь /start чтобы начать сначала!"
            )

            return ConversationHandler.END

        except Exception as e:
            self.logger.error("Ошибка обработки: %s", str(e))
            await update.message.reply_text(
                "⚠️ Произошла ошибка при обработке твоего ответа. "
                "Попробуй отправить голосовое сообщение еще раз или начни заново командой /start."
            )


            return WAITING_VOICE

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Отмена диалога"""
        user = update.message.from_user
        self.logger.info("Пользователь %s отменил диалог.", user.first_name)

        chat_id = update.effective_chat.id
        if chat_id in self.user_data:
            del self.user_data[chat_id]

        await update.message.reply_text(
            "Диалог прерван. Чтобы начать заново, отправь /start"
        )

        return ConversationHandler.END

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработка ошибок"""
        self.logger.error("Ошибка при обработке сообщения: %s", context.error)

        if update.message:
            await update.message.reply_text(
                "⚠️ Произошла непредвиденная ошибка. Пожалуйста, попробуй начать заново командой /start."
            )

    def run(self):
        """Запуск бота с обработчиком диалога"""
        app = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()


        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.start)],
            states={
                WAITING_TEXT: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text),
                    CommandHandler('cancel', self.cancel)
                ],
                WAITING_VOICE: [
                    MessageHandler(filters.VOICE, self.handle_voice),
                    CommandHandler('cancel', self.cancel)
                ],
            },
            fallbacks=[CommandHandler('cancel', self.cancel)],
        )

        app.add_handler(conv_handler)
        app.add_error_handler(self.error_handler)

        app.run_polling()


if __name__ == "__main__":
    bot = SpeechAnalystBot()
    bot.run()
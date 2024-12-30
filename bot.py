import logging
import os
import base64
import json
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from pydub import AudioSegment
import firebase_admin
from firebase_admin import credentials, db
import asyncio
from config import BOT_TOKEN, FIREBASE_DATABASE_URL
from faster_whisper import WhisperModel
import tempfile

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize Firebase
def initialize_firebase():
    try:
        # Get environment variables
        creds_base64 = os.environ.get('FIREBASE_CREDENTIALS_BASE64')
        db_url = os.environ.get('FIREBASE_DATABASE_URL', FIREBASE_DATABASE_URL)
        bot_token = os.environ.get('BOT_TOKEN', BOT_TOKEN)
        
        if creds_base64:
            # For production: use base64 encoded credentials
            creds_json = base64.b64decode(creds_base64).decode('utf-8')
            creds_dict = json.loads(creds_json)
            cred = credentials.Certificate(creds_dict)
            logger.info("Using credentials from environment variables")
        else:
            # For local development: use JSON file
            cred = credentials.Certificate("voicetotext-8b952-firebase-adminsdk-ens30-ebdd1bb0e2.json")
            logger.info("Using credentials from local JSON file")
        
        # Initialize Firebase app
        firebase_admin.initialize_app(cred, {'databaseURL': db_url})
        logger.info("Firebase initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing Firebase: {str(e)}")
        raise

# Initialize Firebase
initialize_firebase()

# Initialize Whisper model (using the small model for efficiency)
model = WhisperModel("small", device="cpu", compute_type="int8")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    welcome_message = (
        "👋 مرحباً بك في بوت تحويل الصوت إلى نص!\n\n"
        "أرسل لي رسالة صوتية وسأقوم بتحويلها إلى نص.\n"
        "الأوامر المتاحة:\n"
        "/start - عرض رسالة الترحيب\n"
        "/help - الحصول على المساعدة"
    )
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    help_text = (
        "🎯 كيفية استخدام البوت:\n\n"
        "1. قم بإرسال رسالة صوتية\n"
        "2. انتظر المعالجة (تستغرق عادةً بضع ثوانٍ)\n"
        "3. استلم النص المحول\n\n"
        "ملاحظة: للحصول على أفضل النتائج، تأكد من جودة الصوت"
    )
    await update.message.reply_text(help_text)

async def process_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process voice messages and convert to text."""
    try:
        # Send initial processing message
        processing_message = await update.message.reply_text("🎵 جاري معالجة الرسالة الصوتية...")

        # Get voice message file
        voice_file = await context.bot.get_file(update.message.voice.file_id)

        # Create temp directory if it doesn't exist
        os.makedirs("temp", exist_ok=True)

        # Use tempfile for safer file handling
        with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as ogg_temp, \
             tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as wav_temp:
            
            # Download voice message
            await voice_file.download_to_drive(ogg_temp.name)

            # Convert ogg to wav using pydub
            audio = AudioSegment.from_ogg(ogg_temp.name)
            audio.export(wav_temp.name, format="wav")

            # Transcribe using Whisper
            segments, _ = model.transcribe(wav_temp.name, language="ar")
            transcribed_text = " ".join([segment.text for segment in segments])

            # Clean up temporary files
            os.unlink(ogg_temp.name)
            os.unlink(wav_temp.name)

        # Store in Firebase
        ref = db.reference('transcriptions')
        ref.push({
            'user_id': update.message.from_user.id,
            'text': transcribed_text,
            'timestamp': {'.sv': 'timestamp'}
        })

        # Send transcription result with a nice format
        formatted_text = (
            "📝 *تم تحويل الصوت إلى نص*\n\n"
            f"{transcribed_text}"
        )
        await processing_message.edit_text(formatted_text, parse_mode='Markdown')

    except Exception as e:
        logger.error(f"Error processing voice message: {str(e)}")
        await update.message.reply_text(
            "❌ عذراً، حدث خطأ أثناء معالجة الرسالة الصوتية. الرجاء المحاولة مرة أخرى."
        )

def main():
    """Start the bot."""
    # Create the Application and pass it your bot's token
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.VOICE, process_voice))

    # Start the Bot
    print("Bot is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()

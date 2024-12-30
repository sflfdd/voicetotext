import logging
import os
import base64
import json
import tempfile
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from pydub import AudioSegment
import firebase_admin
from firebase_admin import credentials, db
import asyncio
from config import BOT_TOKEN, FIREBASE_DATABASE_URL
from vosk import Model, KaldiRecognizer
import wave
import requests

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

# Download and initialize Vosk model
def initialize_vosk():
    model_path = "model"
    if not os.path.exists(model_path):
        os.makedirs(model_path)
        logger.info("Downloading Arabic Vosk model...")
        model_url = "https://alphacephei.com/vosk/models/vosk-model-ar-mgb2-0.4.zip"
        response = requests.get(model_url)
        zip_path = os.path.join(model_path, "model.zip")
        with open(zip_path, "wb") as f:
            f.write(response.content)
        import zipfile
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(model_path)
        os.remove(zip_path)
        logger.info("Model downloaded and extracted")
    
    return Model(os.path.join(model_path, "vosk-model-ar-mgb2-0.4"))

# Initialize Vosk model
model = initialize_vosk()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('مرحباً! أرسل لي رسالة صوتية وسأقوم بتحويلها إلى نص.')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('أرسل لي رسالة صوتية وسأقوم بتحويلها إلى نص.')

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Get voice message file
        voice = await context.bot.get_file(update.message.voice.file_id)
        
        # Create temp directory if it doesn't exist
        if not os.path.exists('temp'):
            os.makedirs('temp')
        
        # Download voice file
        voice_ogg = f"temp/{voice.file_id}.ogg"
        voice_wav = f"temp/{voice.file_id}.wav"
        await voice.download_to_drive(voice_ogg)
        
        # Convert OGG to WAV
        audio = AudioSegment.from_ogg(voice_ogg)
        audio = audio.set_channels(1)  # Convert to mono
        audio = audio.set_frame_rate(16000)  # Set sample rate to 16kHz
        audio.export(voice_wav, format="wav")
        
        # Perform speech recognition
        wf = wave.open(voice_wav, "rb")
        rec = KaldiRecognizer(model, wf.getframerate())
        
        text = ""
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text += result.get("text", "") + " "
        
        final_result = json.loads(rec.FinalResult())
        text += final_result.get("text", "")
        text = text.strip()
        
        if not text:
            text = "لم أتمكن من فهم الكلام في هذا التسجيل"
        
        # Store in Firebase
        ref = db.reference('transcriptions')
        ref.push({
            'user_id': update.message.from_user.id,
            'text': text,
            'timestamp': {'.sv': 'timestamp'}
        })
        
        # Send transcription to user
        await update.message.reply_text(f"النص: {text}")
        
        # Cleanup temp files
        wf.close()
        os.remove(voice_ogg)
        os.remove(voice_wav)
        
    except Exception as e:
        logger.error(f"Error processing voice message: {str(e)}")
        await update.message.reply_text("عذراً، حدث خطأ أثناء معالجة الرسالة الصوتية. الرجاء المحاولة مرة أخرى.")

def main():
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.VOICE & ~filters.COMMAND, handle_voice))
    
    # Run the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()

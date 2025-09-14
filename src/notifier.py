import telegram
from .config import TELEGRAM_TOKEN, CHAT_ID

# Crear bot solo si el token es válido
if TELEGRAM_TOKEN and TELEGRAM_TOKEN != "dummy_token_for_testing":
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
else:
    bot = None

async def send_message(text):
    if bot is None:
        print(f"📱 [TELEGRAM MOCK] {text}")
        return True
        
    try:
        await bot.send_message(chat_id=CHAT_ID, text=text)
        return True
    except Exception as e:
        print(f"❌ Error enviando mensaje de Telegram: {e}")
        return False

import telegram
from config import TELEGRAM_TOKEN, CHAT_ID

bot = telegram.Bot(token=TELEGRAM_TOKEN)

async def send_message(text):
    await bot.send_message(chat_id=CHAT_ID, text=text)

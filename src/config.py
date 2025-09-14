import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"

# Para testing, no fallar si las variables no están configuradas
if not TELEGRAM_TOKEN and not os.getenv("TESTING"):
    print("⚠️ Warning: TELEGRAM_TOKEN no configurado")
    TELEGRAM_TOKEN = "dummy_token_for_testing"

if not CHAT_ID and not os.getenv("TESTING"):
    print("⚠️ Warning: TELEGRAM_CHAT_ID no configurado") 
    CHAT_ID = "dummy_chat_id_for_testing"

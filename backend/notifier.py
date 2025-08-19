# notifier.py

import telegram
import asyncio
import os

# SUBSTITUA PELO SEU TOKEN E CHAT ID
BOT_TOKEN = "SEU_TOKEN_AQUI"
CHAT_ID = "SEU_CHAT_ID_AQUI"

class TelegramNotifier:
    def __init__(self):
        self.bot = telegram.Bot(token=BOT_TOKEN)
        
    async def send_alert(self, message, image_path=None):
        try:
            # Envia a mensagem de texto
            await self.bot.send_message(chat_id=CHAT_ID, text=message)
            
            # Se houver imagem, envia a foto
            if image_path and os.path.exists(image_path):
                with open(image_path, 'rb') as photo:
                    await self.bot.send_photo(chat_id=CHAT_ID, photo=photo)
            
            print(f"[NOTIFICADOR] Alerta enviado: {message}")
        except Exception as e:
            print(f"ERRO ao enviar notificação: {e}")

# Exemplo de uso
async def main():
    notifier = TelegramNotifier()
    await notifier.send_alert("Teste de notificação do Phoenix Vision!")

if __name__ == '__main__':
    asyncio.run(main())
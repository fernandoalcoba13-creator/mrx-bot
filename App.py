import os
import asyncio
from flask import Flask, request, render_template_string
from telegram import Bot

app = Flask(__name__)

# Configuración desde variables de entorno
TOKEN = os.getenv("TELEGRAM_TOKEN")
# IDs de tus 60 grupos separados por coma en Railway
GROUP_IDS = os.getenv("GROUP_IDS", "").split(",")

async def send_broadcast(message):
    bot = Bot(token=TOKEN)
    for group_id in GROUP_IDS:
        try:
            # Envío con pequeño delay para evitar bloqueos de Telegram
            await bot.send_message(chat_id=group_id.strip(), text=message, parse_mode='HTML')
            await asyncio.sleep(0.5) 
        except Exception as e:
            print(f"Error en {group_id}: {e}")

@app.route('/', methods=['GET', 'POST'])
def index():
    status = ""
    if request.method == 'POST':
        msg = request.form.get('message')
        if msg:
            asyncio.run(send_broadcast(msg))
            status = "🚀 ¡Anuncio enviado con éxito!"
    
    return render_template_string('''
        <body style="font-family:sans-serif; text-align:center; padding-top:50px; background:#1a1a1a; color:white;">
            <h1>MR X BOT - Control de Anuncios</h1>
            <form method="post">
                <textarea name="message" rows="6" cols="50" style="border-radius:10px; padding:10px;" placeholder="Escribe el mensaje para tus 60 grupos..."></textarea><br><br>
                <button type="submit" style="padding:10px 20px; border-radius:5px; background:#f05423; color:white; border:none; cursor:pointer;">DIFUNDIR AHORA</button>
            </form>
            <p style="color:#00ff00;">{{status}}</p>
        </body>
    ''', status=status)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
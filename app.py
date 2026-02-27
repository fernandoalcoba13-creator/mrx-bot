import os
import asyncio
from flask import Flask, request, render_template_string
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

app = Flask(__name__)

TOKEN = os.getenv("TELEGRAM_TOKEN")
GROUP_IDS = os.getenv("GROUP_IDS", "").split(",")

async def send_broadcast(message):
    bot = Bot(token=TOKEN)
    
    # AQUÍ CREAMOS LOS BOTONES TIPO CONTROLLER BOT
    keyboard = [
        [
            InlineKeyboardButton("🌐 Ver Tools 3D", url="https://tools.kmorra3d.com"),
            InlineKeyboardButton("🎓 Academia", url="https://www.academiakmorra.com")
        ],
        [InlineKeyboardButton("📸 Instagram", url="https://www.instagram.com/kmorra3d")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    for group_id in GROUP_IDS:
        try:
            await bot.send_message(
                chat_id=group_id.strip(), 
                text=message, 
                parse_mode='HTML',
                reply_markup=reply_markup  # Esto añade los botones al mensaje
            )
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
            status = "🚀 ¡Anuncio con botones enviado!"
    
    return render_template_string('''
        <body style="font-family:sans-serif; text-align:center; padding-top:50px; background:#1a1a1a; color:white;">
            <h1>MR X BOT - Estilo Controller Bot</h1>
            <p>El mensaje se enviará con botones automáticos a la Web y Academia.</p>
            <form method="post">
                <textarea name="message" rows="6" cols="50" style="border-radius:10px; padding:10px;" 
                placeholder="Escribí el texto del anuncio aquí..."></textarea><br><br>
                <button type="submit" style="padding:15px 30px; border-radius:5px; background:#f05423; color:white; border:none; cursor:pointer; font-weight:bold;">
                    ENVIAR A TODOS LOS GRUPOS
                </button>
            </form>
            <p style="color:#00ff00;">{{status}}</p>
        </body>
    ''', status=status)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

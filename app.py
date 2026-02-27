import os
import asyncio
from flask import Flask, request, render_template_string
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

app = Flask(__name__)

TOKEN = os.getenv("TELEGRAM_TOKEN")
GROUP_IDS = os.getenv("GROUP_IDS", "").split(",")

async def send_broadcast(message):
    bot = Bot(token=TOKEN)
    
    # CONFIGURACIÓN DE BOTONES CON TUS LINKS EXACTOS
    keyboard = [
        [InlineKeyboardButton("📊 CALCULADORA DE COSTOS", url="https://tools.kmorra3d.com/calculadora-3d.html")],
        [InlineKeyboardButton("🛡️ MARCA TUS STL", url="https://tools.kmorra3d.com/stl-watermark.html")],
        [InlineKeyboardButton("🤖 DIAGNÓSTICO DE FALLAS IA", url="https://tools.kmorra3d.com/diagnostico_fallos.html")],
        [InlineKeyboardButton("🌈 CALCULADORA MULTICOLOR", url="https://tools.kmorra3d.com/calculadora-ams.html")],
        [InlineKeyboardButton("🎓 APRENDE A DISEÑAR", url="https://www.academiakmorra.com")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    for group_id in GROUP_IDS:
        try:
            await bot.send_message(
                chat_id=group_id.strip(), 
                text=message, 
                parse_mode='HTML',
                reply_markup=reply_markup
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
            status = "🚀 ¡Anuncio enviado con éxito!"
    
    return render_template_string('''
        <body style="font-family:sans-serif; text-align:center; padding-top:50px; background:#1a1a1a; color:white;">
            <h1 style="color:#f05423;">MR X BOT - Control Panel</h1>
            <p>Escribí el texto llamativo y el bot le pondrá los 5 botones con sus links.</p>
            <form method="post">
                <textarea name="message" rows="8" cols="60" style="border-radius:10px; padding:15px; border:none; font-size:14px;" 
                placeholder="Escribí el anuncio aquí..."></textarea><br><br>
                <button type="submit" style="padding:15px 30px; border-radius:8px; background:#f05423; color:white; border:none; cursor:pointer; font-weight:bold; font-size:16px;">
                    DIFUNDIR AHORA 🚀
                </button>
            </form>
            <p style="color:#00ff00; font-weight:bold;">{{status}}</p>
        </body>
    ''', status=status)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

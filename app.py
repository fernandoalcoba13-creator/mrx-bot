import os
import asyncio
from flask import Flask, request, render_template_string
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, MessageHandler, filters

app = Flask(__name__)

TOKEN = os.getenv("TELEGRAM_TOKEN")
GROUP_IDS = os.getenv("GROUP_IDS", "").split(",")

# CONFIGURACIÓN DE LOS BOTONES (Para reutilizar en anuncios y bienvenidas)
def get_main_buttons():
    keyboard = [
        [InlineKeyboardButton("📊 CALCULADORA DE COSTOS", url="https://tools.kmorra3d.com")],
        [InlineKeyboardButton("🛡️ MARCA TUS STL", url="https://tools.kmorra3d.com")],
        [InlineKeyboardButton("🤖 DIAGNÓSTICO DE FALLAS IA", url="https://tools.kmorra3d.com")],
        [InlineKeyboardButton("🌈 CALCULADORA MULTICOLOR", url="https://tools.kmorra3d.com")],
        [InlineKeyboardButton("🎓 APRENDE A DISEÑAR", url="https://www.academiakmorra.com")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def send_broadcast(message):
    bot = Bot(token=TOKEN)
    reply_markup = get_main_buttons()
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
            status = "🚀 ¡Difusión enviada con éxito!"
    
    return render_template_string('''
        <body style="font-family:sans-serif; text-align:center; padding-top:50px; background:#1a1a1a; color:white;">
            <h1 style="color:#f05423;">MR X BOT - Panel Pro</h1>
            <p>El mensaje se enviará con el diseño de 5 botones configurado.</p>
            <form method="post">
                <textarea name="message" rows="8" cols="60" style="border-radius:10px; padding:15px; border:none;" 
                placeholder="Escribí el texto llamativo aquí..."></textarea><br><br>
                <button type="submit" style="padding:15px 30px; border-radius:10px; background:#f05423; color:white; border:none; cursor:pointer; font-size:16px; font-weight:bold;">
                    DISPARAR ANUNCIO 🚀
                </button>
            </form>
            <p style="color:#00ff00;">{{status}}</p>
        </body>
    ''', status=status)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

import os
import asyncio
from flask import Flask, render_template_string
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

TOKEN = os.getenv("TELEGRAM_TOKEN")
GROUP_IDS = os.getenv("GROUP_IDS", "").split(",")

async def send_automatic_broadcast():
    if not TOKEN or not GROUP_IDS:
        return

    bot = Bot(token=TOKEN)
    
    # BUSCAMOS EL ARCHIVO DENTRO DE LA CARPETA DEL BOT
    foto_path = "banner.jpg" 
    
    texto = (
        "✨ <b>¿LISTO PARA ACELERAR TU PRODUCCIÓN 3D?</b> ✨\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "En la <b>Comunidad MR X</b> te damos las herramientas para que tu taller no pare nunca:\n\n"
        "📊 <b>Calculadoras:</b> Costos exactos y sistema AMS.\n"
        "🛡️ <b>Protección:</b> Marca de agua automática para tus STL.\n"
        "🤖 <b>Diagnóstico IA:</b> Inteligencia Artificial para resolver fallas.\n\n"
        "⬇️ <b>Seleccioná una herramienta para empezar:</b>"
    )
    
    keyboard = [
        [InlineKeyboardButton("📊 Calculadora de Costos PRO", url="https://tools.kmorra3d.com/calculadora-3d.html")],
        [InlineKeyboardButton("🌈 Calculadora AMS / Multicolor", url="https://tools.kmorra3d.com/calculadora-ams.html")],
        [InlineKeyboardButton("🛡️ Proteger mis Diseños (Watermark)", url="https://tools.kmorra3d.com/stl-watermark.html")],
        [InlineKeyboardButton("🤖 IA: Diagnóstico de Fallas", url="https://tools.kmorra3d.com/diagnostico_fallos.html")],
        [InlineKeyboardButton("🎓 Academia Kmorra: Aprender a Diseñar", url="https://www.academiakmorra.com")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    for group_id in GROUP_IDS:
        group_id = group_id.strip()
        if not group_id: continue
        try:
            # ENVIAMOS EL ARCHIVO LOCAL (Telegram lo recibe directo del servidor)
            if os.path.exists(foto_path):
                with open(foto_path, 'rb') as photo:
                    await bot.send_photo(
                        chat_id=group_id, 
                        photo=photo, 
                        caption=texto, 
                        parse_mode='HTML', 
                        reply_markup=reply_markup
                    )
            else:
                # Si por alguna razón no encuentra el archivo, manda el texto
                await bot.send_message(chat_id=group_id, text=texto, parse_mode='HTML', reply_markup=reply_markup)
        except Exception as e:
            print(f"Error: {e}")
        await asyncio.sleep(1)

scheduler = BackgroundScheduler()
# Cuando veas que funciona, cambiá 'minutes=1' por 'hours=8'
scheduler.add_job(lambda: asyncio.run(send_automatic_broadcast()), 'interval', minutes=1)
scheduler.start()

@app.route('/')
def home():
    return "🚀 MR X BOT - Enviando desde archivo local"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

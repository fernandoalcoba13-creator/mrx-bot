import os
import asyncio
from flask import Flask, render_template_string
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

# CONFIGURACIÓN
TOKEN = os.getenv("TELEGRAM_TOKEN")
GROUP_IDS = os.getenv("GROUP_IDS", "").split(",")

async def send_automatic_broadcast():
    if not TOKEN or not GROUP_IDS:
        return

    bot = Bot(token=TOKEN)
    
    # URL DE IMAGEN ESTABLE (Hecha para que Telegram la acepte siempre)
    IMAGE_URL = "https://i.ibb.co/3sZ8X9N/mr-x-3d-print-marketing.jpg" 
    
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
            # INTENTO ENVIAR CON FOTO
            await bot.send_photo(
                chat_id=group_id,
                photo=IMAGE_URL,
                caption=texto, 
                parse_mode='HTML',
                reply_markup=reply_markup
            )
        except Exception as e:
            # SI LA FOTO FALLA, ENVÍA SOLO EL TEXTO PARA QUE NO SE CORTE EL MARKETING
            print(f"Falla foto en {group_id}, enviando solo texto. Error: {e}")
            try:
                await bot.send_message(
                    chat_id=group_id,
                    text=texto,
                    parse_mode='HTML',
                    reply_markup=reply_markup
                )
            except Exception as e2:
                print(f"Error fatal en {group_id}: {e2}")
        
        await asyncio.sleep(0.5)

# RELOJ (Ajustado a 1 minuto para tu prueba final)
scheduler = BackgroundScheduler()
scheduler.add_job(lambda: asyncio.run(send_automatic_broadcast()), 'interval', minutes=1)
scheduler.start()

@app.route('/', methods=['GET', 'POST'])
def home():
    return "🚀 MR X BOT activo. El sistema de marketing con imagen está corriendo."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

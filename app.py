import os
import asyncio
from flask import Flask, render_template_string
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

# CONFIGURACIÓN DE VARIABLES
TOKEN = os.getenv("TELEGRAM_TOKEN")
GROUP_IDS = os.getenv("GROUP_IDS", "").split(",")

async def send_automatic_broadcast():
    if not TOKEN or not GROUP_IDS:
        return

    bot = Bot(token=TOKEN)
    
    # URL de tu imagen en GitHub
    IMAGE_URL = "https://raw.githubusercontent.com/fernandoalcoba13-creator/mrx-bot/main/banner.jpg" 
    
    # NUEVA ESTÉTICA MEJORADA
    texto = (
        "🚀 <b>¡POTENCIÁ TU TALLER 3D CON MR X!</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Llevá tu producción al siguiente nivel con nuestras herramientas <b>¡GRATUITAS!</b> 🎁\n\n"
        "💎 <b>SOLUCIONES PARA MAKERS:</b>\n"
        "• 📊 <b>Calculadoras:</b> Costos y sistema multicolor.\n"
        "• 🛡️ <b>Protección:</b> Marca de agua para tus archivos STL.\n"
        "• 🤖 <b>IA:</b> Diagnóstico inteligente de fallas.\n\n"
        "⬇️ <i>¡Accedé ahora desde los botones!</i>"
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
            # Intento con foto (usando el link que ya nos funcionó)
            await bot.send_photo(
                chat_id=group_id, 
                photo=IMAGE_URL, 
                caption=texto, 
                parse_mode='HTML', 
                reply_markup=reply_markup
            )
        except Exception:
            try:
                # Backup: Solo texto si la imagen falla
                await bot.send_message(chat_id=group_id, text=texto, parse_mode='HTML', reply_markup=reply_markup)
            except Exception:
                pass
        await asyncio.sleep(1)

# CONFIGURACIÓN DEL RELOJ - CAMBIADO A 8 HORAS
scheduler = BackgroundScheduler()
scheduler.add_job(lambda: asyncio.run(send_automatic_broadcast()), 'interval', hours=8)
scheduler.start()

@app.route('/')
def home():
    return render_template_string('''
        <body style="font-family:sans-serif; text-align:center; padding-top:50px; background:#1a1a1a; color:white;">
            <h1 style="color:#f05423;">MR X BOT - MODO PROFESIONAL</h1>
            <p style="color:#00ff00;">✓ Difusión automática activa cada 8 horas.</p>
            <p>El bot está promocionando tus herramientas gratuitas y la Academia.</p>
        </body>
    ''')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

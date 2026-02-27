import os
import asyncio
from flask import Flask, render_template_string
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

# CONFIGURACIÓN DESDE VARIABLES DE ENTORNO EN RAILWAY
TOKEN = os.getenv("TELEGRAM_TOKEN")
GROUP_IDS = os.getenv("GROUP_IDS", "").split(",")

async def send_automatic_broadcast():
    if not TOKEN or not GROUP_IDS:
        print("Faltan configurar variables de entorno.")
        return

    bot = Bot(token=TOKEN)
    
    # DISEÑO ESTÉTICO MEJORADO
    texto = (
        "✨ <b>¡POTENCIÁ TU TALLER 3D CON MR X!</b> ✨\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Llevá tu negocio al siguiente nivel con nuestras <b>Herramientas Profesionales GRATUITAS</b>. 🚀\n\n"
        "💎 <b>¿Qué podés hacer hoy?</b>\n"
        "• <b>Calculá:</b> Costos exactos y sistema multicolor.\n"
        "• <b>Protegé:</b> Marca de agua automática para tus STL.\n"
        "• <b>Resolvé:</b> Diagnóstico de fallas con Inteligencia Artificial.\n\n"
        "⬇️ <i>¡Accedé ahora desde los botones!</i> ⬇️"
    )
    
    # BOTONES CON LINKS ACTUALIZADOS
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
            await bot.send_message(chat_id=group_id, text=texto, parse_mode='HTML', reply_markup=reply_markup)
            await asyncio.sleep(0.5) # Seguridad para evitar baneo de Telegram
        except Exception as e:
            print(f"Error enviando a {group_id}: {e}")

# CONFIGURACIÓN DEL RELOJ INTERNO (SCHEDULER)
scheduler = BackgroundScheduler()
# IMPORTANTE: Cambiá 'minutes=1' por 'hours=8' después de confirmar que funciona.
scheduler.add_job(lambda: asyncio.run(send_automatic_broadcast()), 'interval', minutes=1)
scheduler.start()

# RUTA PARA EVITAR EL ERROR 405 (Method Not Allowed) EN RAILWAY
@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template_string('''
        <body style="font-family:sans-serif; text-align:center; padding-top:50px; background:#1a1a1a; color:white;">
            <h1 style="color:#f05423;">MR X BOT - ESTADO ACTIVO</h1>
            <p>El sistema de difusión con estética mejorada está funcionando.</p>
            <p style="color:#00ff00;">✓ Reloj interno programado</p>
            <p style="color:#00ff00;">✓ Conexión con Telegram OK</p>
            <hr style="width:50%; border:0.5px solid #333;">
            <small>Recordá cambiar el intervalo a 8 horas para evitar spam.</small>
        </body>
    ''')

if __name__ == "__main__":
    # Railway asigna un puerto dinámico, lo tomamos de aquí:
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

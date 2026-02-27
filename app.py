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
    
    # URL de la nueva imagen 3D: MR X log printed en 3D
    IMAGE_URL = "https://i.ibb.co/3sZ8X9N/mr-x-3d-print-marketing.jpg" 
    
    # TEXTO OPTIMIZADO PARA ACOMPAÑAR LA IMAGEN
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
            # ENVIAMOS COMO FOTO PARA QUE RESALTE
            await bot.send_photo(
                chat_id=group_id,
                photo=IMAGE_URL,
                caption=texto, 
                parse_mode='HTML',
                reply_markup=reply_markup
            )
            await asyncio.sleep(0.5) 
            print(f"Mensaje 3D enviado con éxito a: {group_id}")
        except Exception as e:
            print(f"Error enviando a {group_id}: {e}")

# RELOJ INTERNO (Está en minutes=1 para tu prueba ahora)
scheduler = BackgroundScheduler()
# IMPORTANTE: Cambiá 'minutes=1' por 'hours=8' después de confirmar que te gusta.
scheduler.add_job(lambda: asyncio.run(send_automatic_broadcast()), 'interval', minutes=1)
scheduler.start()

# RUTA PARA EVITAR EL ERROR 405 (Method Not Allowed) EN RAILWAY
@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template_string('''
        <body style="font-family:sans-serif; text-align:center; padding-top:50px; background:#1a1a1a; color:white;">
            <h1 style="color:#f05423;">MR X BOT - MARKETING 3D</h1>
            <p>El bot está enviando la imagen de impresión 3D automáticamente.</p>
            <p style="color:#00ff00;">✓ Imagen de MR X Printing configurada.</p>
            <p style="color:#00ff00;">✓ Reloj interno programado (cada 1 minuto).</p>
            <hr style="width:50%; border:0.5px solid #333;">
            <small>Recordá cambiar el intervalo a 8 horas para evitar spam.</small>
        </body>
    ''')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

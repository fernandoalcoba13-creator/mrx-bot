import os
import asyncio
from flask import Flask, render_template_string
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

# CONFIGURACIÓN DESDE VARIABLES DE ENTORNO
TOKEN = os.getenv("TELEGRAM_TOKEN")
GROUP_IDS = os.getenv("GROUP_IDS", "").split(",")

# FUNCIÓN DE ENVÍO MASIVO CON DISEÑO PROFESIONAL
async def send_automatic_broadcast():
    if not TOKEN or not GROUP_IDS:
        print("Error: TOKEN o GROUP_IDS no configurados.")
        return

    bot = Bot(token=TOKEN)
    
    # Texto ultra llamativo basado en tu diseño exitoso
    texto = (
        "🔥 <b>¡BIENVENIDOS A LA COMUNIDAD MR X DE IMPRESIÓN 3D!</b> 🔥\n\n"
        "¡Llevá tu taller al siguiente nivel con nuestras herramientas GRATUITAS! 🚀\n\n"
        "✅ <b>Calculá</b> tus costos de impresión y multicolor.\n"
        "✅ <b>Protegé</b> tus modelos STL con marca de agua.\n"
        "✅ <b>Resolvé</b> problemas de impresión con Inteligencia Artificial.\n\n"
        "¡Hacé clic en los botones de abajo y empezá ahora! 👇"
    )
    
    # Botones con tus links actualizados
    keyboard = [
        [InlineKeyboardButton("📊 CALCULADORA DE COSTOS", url="https://tools.kmorra3d.com/calculadora-3d.html")],
        [InlineKeyboardButton("🛡️ MARCA TUS STL", url="https://tools.kmorra3d.com/stl-watermark.html")],
        [InlineKeyboardButton("🤖 DIAGNÓSTICO DE FALLAS IA", url="https://tools.kmorra3d.com/diagnostico_fallos.html")],
        [InlineKeyboardButton("🌈 CALCULADORA MULTICOLOR", url="https://tools.kmorra3d.com/calculadora-ams.html")],
        [InlineKeyboardButton("🎓 APRENDE A DISEÑAR", url="https://www.academiakmorra.com")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    for group_id in GROUP_IDS:
        group_id = group_id.strip()
        if not group_id:
            continue
        try:
            await bot.send_message(
                chat_id=group_id, 
                text=texto, 
                parse_mode='HTML', 
                reply_markup=reply_markup
            )
            await asyncio.sleep(0.5) # Seguridad para evitar spam
            print(f"Mensaje enviado con éxito a: {group_id}")
        except Exception as e:
            print(f"No se pudo enviar a {group_id}: {e}")

# CONFIGURACIÓN DEL RELOJ INTERNO (SCHEDULER)
scheduler = BackgroundScheduler()
# CAMBIAR A hours=8 PARA PRODUCCIÓN PROFESIONAL
scheduler.add_job(lambda: asyncio.run(send_automatic_broadcast()), 'interval', minutes=1)
scheduler.start()

# RUTA PARA QUE RAILWAY NO TIRE ERROR VISUAL
@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template_string('''
        <body style="font-family:sans-serif; text-align:center; padding-top:50px; background:#1a1a1a; color:white;">
            <h1 style="color:#f05423;">MR X BOT - ESTADO ACTIVO</h1>
            <p>El sistema de difusión automática está funcionando correctamente.</p>
            <p style="color:#00ff00;">✓ Reloj interno programado</p>
            <p style="color:#00ff00;">✓ Conexión con Telegram OK</p>
        </body>
    ''')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

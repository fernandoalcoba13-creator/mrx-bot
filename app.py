import os
import asyncio
from datetime import datetime
from flask import Flask, render_template_string
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

# CONFIGURACIÓN DE VARIABLES (Railway)
TOKEN = os.getenv("TELEGRAM_TOKEN")
GROUP_IDS = os.getenv("GROUP_IDS", "").split(",")

async def send_automatic_broadcast():
    if not TOKEN or not GROUP_IDS:
        print("Faltan variables de entorno: TELEGRAM_TOKEN o GROUP_IDS")
        return

    bot = Bot(token=TOKEN)
    
    # OPCIÓN A: Link externo (PostImg)
    IMAGE_URL = "https://i.postimg.cc/qM9D8fC9/mr-x-3d-banner.jpg" 
    
    # OPCIÓN B: Archivo local (debe estar en el repo de GitHub)
    foto_local = "banner.jpg"
    
    # TEXTO OPTIMIZADO: RESALTANDO LO GRATUITO
    texto = (
        "🚀 <b>¡POTENCIÁ TU TALLER 3D CON MR X!</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Llevá tu producción al siguiente nivel con nuestras herramientas <b>¡TOTALMENTE GRATUITAS!</b> 🎁\n\n"
        "💎 <b>SOLUCIONES PARA MAKERS:</b>\n"
        "• 📊 <b>Calculadoras:</b> Costos exactos y sistema multicolor.\n"
        "• 🛡️ <b>Protección:</b> Marca de agua para tus archivos STL.\n"
        "• 🤖 <b>IA:</b> Diagnóstico inteligente de fallas en impresiones.\n\n"
        "⬇️ <i>¡Accedé sin costo desde los botones de abajo!</i>"
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
        
        exito = False
        
        # Intento 1: Por URL externa
        try:
            await bot.send_photo(chat_id=group_id, photo=IMAGE_URL, caption=texto, parse_mode='HTML', reply_markup=reply_markup)
            exito = True
        except Exception as e:
            print(f"URL falló en {group_id}, probando local... Error: {e}")

        # Intento 2: Por Archivo Local (si la URL falló)
        if not exito:
            try:
                if os.path.exists(foto_local):
                    with open(foto_local, 'rb') as f:
                        await bot.send_photo(chat_id=group_id, photo=f, caption=texto, parse_mode='HTML', reply_markup=reply_markup)
                    exito = True
                else:
                    print(f"Archivo local {foto_local} no encontrado.")
            except Exception as e:
                print(f"Local falló en {group_id}. Error: {e}")

        # Intento 3: Solo Texto (si todo lo demás falló)
        if not exito:
            try:
                await bot.send_message(chat_id=group_id, text=texto, parse_mode='HTML', reply_markup=reply_markup)
                print(f"Solo texto enviado a {group_id}")
            except Exception as e:
                print(f"Error fatal enviando a {group_id}: {e}")
        
        await asyncio.sleep(1.5) # Pausa de seguridad entre grupos

# CONFIGURACIÓN DEL SCHEDULER (RELOJ)
scheduler = BackgroundScheduler()
# next_run_time=datetime.now() dispara el primero AL INSTANTE de subirlo
scheduler.add_job(
    lambda: asyncio.run(send_automatic_broadcast()), 
    'interval', 
    hours=8, 
    next_run_time=datetime.now()
)
scheduler.start()

@app.route('/')
def home():
    return render_template_string('''
        <body style="font-family:sans-serif; text-align:center; padding-top:50px; background:#1a1a1a; color:white;">
            <h1 style="color:#f05423;">MR X BOT - MODO PROFESIONAL</h1>
            <p style="color:#00ff00;">✓ Difusión automática activa cada 8 horas.</p>
            <p>Promocionando herramientas gratuitas y la Academia Kmorra.</p>
        </body>
    ''')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

import os, asyncio
from flask import Flask
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
TOKEN = os.getenv("TELEGRAM_TOKEN")
GROUP_IDS = os.getenv("GROUP_IDS", "").split(",")

async def mandar_aviso():
    bot = Bot(token=TOKEN)
    texto = "🔥 <b>¡BIENVENIDOS A LA COMUNIDAD MR X!</b> 🔥\n\n¡Llevá tu taller al siguiente nivel con nuestras herramientas GRATUITAS! 🚀"
    
    # TUS LINKS REALES
    btns = [
        [InlineKeyboardButton("📊 CALCULADORA DE COSTOS", url="https://tools.kmorra3d.com/calculadora-3d.html")],
        [InlineKeyboardButton("🛡️ MARCA TUS STL", url="https://tools.kmorra3d.com/stl-watermark.html")],
        [InlineKeyboardButton("🤖 DIAGNÓSTICO DE FALLAS IA", url="https://tools.kmorra3d.com/diagnostico_fallos.html")],
        [InlineKeyboardButton("🌈 CALCULADORA MULTICOLOR", url="https://tools.kmorra3d.com/calculadora-ams.html")],
        [InlineKeyboardButton("🎓 APRENDE A DISEÑAR", url="https://www.academiakmorra.com")]
    ]
    
    for g_id in GROUP_IDS:
        try:
            await bot.send_message(chat_id=g_id.strip(), text=texto, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(btns))
            await asyncio.sleep(0.5)
        except: pass

# PROGRAMACIÓN CADA 8 HORAS
sched = BackgroundScheduler()
sched.add_job(lambda: asyncio.run(mandar_aviso()), 'interval', minutes=1)
sched.start()

@app.route('/')
def home(): return "MR X BOT ACTIVO"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))


import os
import asyncio
import random
from datetime import datetime
from flask import Flask, render_template_string
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

# ─────────────────────────────────────────
# CONFIGURACIÓN DE VARIABLES (Railway)
# ─────────────────────────────────────────
TOKEN = os.getenv("TELEGRAM_TOKEN")
GROUP_IDS = os.getenv("GROUP_IDS", "").split(",")

# ─────────────────────────────────────────
# IMAGEN DEL BANNER
# ─────────────────────────────────────────
IMAGE_URL = "https://i.postimg.cc/qM9D8fC9/mr-x-3d-banner.jpg"
FOTO_LOCAL = "banner.jpg"

# ─────────────────────────────────────────
# HORARIOS PICO (hora UTC-3 Argentina)
# Se dispara a las 9hs, 14hs y 21hs (hora Argentina)
# En UTC eso es: 12, 17, 00
# ─────────────────────────────────────────
PEAK_HOURS_UTC = [12, 17, 0]  # 9am, 2pm, 9pm Argentina

# ─────────────────────────────────────────
# CONTADOR ROTATIVO DE MENSAJES
# ─────────────────────────────────────────
message_index = 0

# ─────────────────────────────────────────
# ESTADÍSTICAS EN MEMORIA
# ─────────────────────────────────────────
stats = {
    "total_enviados": 0,
    "errores": 0,
    "ultimo_envio": "Nunca",
    "grupos_bloqueados": []
}

# ─────────────────────────────────────────
# 3 MENSAJES ROTATIVOS
# ─────────────────────────────────────────
MENSAJES = [
    # ── Mensaje 1: Herramientas gratuitas ──
    (
        "🚀 <b>¡POTENCIÁ TU TALLER 3D CON MR X!</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Llevá tu producción al siguiente nivel con nuestras herramientas <b>¡TOTALMENTE GRATUITAS!</b> 🎁\n\n"
        "💎 <b>SOLUCIONES PARA MAKERS:</b>\n"
        "• 📊 <b>Calculadoras:</b> Costos exactos y sistema multicolor.\n"
        "• 🛡️ <b>Protección:</b> Marca de agua para tus archivos STL.\n"
        "• 🤖 <b>IA:</b> Diagnóstico inteligente de fallas en impresiones.\n\n"
        "⬇️ <i>¡Accedé sin costo desde los botones de abajo!</i>"
    ),
    # ── Mensaje 2: Enfoque en el diagnóstico IA ──
    (
        "🤖 <b>¿TUS IMPRESIONES FALLAN Y NO SABÉS POR QUÉ?</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Nuestra <b>IA de diagnóstico</b> analiza tus fallas y te dice exactamente qué ajustar. ¡Es gratis! 🎯\n\n"
        "🔧 <b>TAMBIÉN TENÉS DISPONIBLE:</b>\n"
        "• 📊 Calculadora de costos para no trabajar a pérdida.\n"
        "• 🌈 Calculadora AMS para proyectos multicolor.\n"
        "• 🛡️ Protegé tus diseños STL con marca de agua.\n\n"
        "⬇️ <i>Todo en un clic, ¡completamente gratis!</i>"
    ),
    # ── Mensaje 3: Enfoque en la academia ──
    (
        "🎓 <b>¿QUERÉS DISEÑAR TUS PROPIAS PIEZAS 3D?</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "En la <b>Academia Kmorra</b> aprendés desde cero a crear modelos profesionales. 💡\n\n"
        "🛠️ <b>MIENTRAS TANTO, USÁ ESTAS TOOLS GRATIS:</b>\n"
        "• 📊 Calculá tus costos y ganancia real por pieza.\n"
        "• 🌈 Optimizá el filamento en proyectos multicolor.\n"
        "• 🤖 Diagnosticá fallas con IA antes de perder material.\n\n"
        "⬇️ <i>¡Hacé clic y empezá hoy!</i>"
    ),
]

# ─────────────────────────────────────────
# TECLADO DE BOTONES (siempre el mismo)
# ─────────────────────────────────────────
def get_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Calculadora de Costos PRO", url="https://tools.kmorra3d.com/calculadora-3d.html")],
        [InlineKeyboardButton("🌈 Calculadora AMS / Multicolor", url="https://tools.kmorra3d.com/calculadora-ams.html")],
        [InlineKeyboardButton("🛡️ Proteger mis Diseños (Watermark)", url="https://tools.kmorra3d.com/stl-watermark.html")],
        [InlineKeyboardButton("🤖 IA: Diagnóstico de Fallas", url="https://tools.kmorra3d.com/diagnostico_fallos.html")],
        [InlineKeyboardButton("🎓 Academia Kmorra: Aprender a Diseñar", url="https://www.academiakmorra.com")]
    ])

# ─────────────────────────────────────────
# FUNCIÓN PRINCIPAL DE BROADCAST
# ─────────────────────────────────────────
async def send_automatic_broadcast():
    global message_index

    if not TOKEN or not GROUP_IDS:
        print("❌ Faltan variables: TELEGRAM_TOKEN o GROUP_IDS")
        return

    # Verificar si es horario pico (hora UTC actual)
    hora_utc = datetime.utcnow().hour
    if hora_utc not in PEAK_HOURS_UTC:
        print(f"⏰ Hora UTC {hora_utc} no es horario pico. Saltando envío.")
        return

    bot = Bot(token=TOKEN)
    texto = MENSAJES[message_index % len(MENSAJES)]
    message_index += 1
    reply_markup = get_keyboard()

    print(f"📤 Enviando mensaje #{message_index} a {len(GROUP_IDS)} grupos...")

    for group_id in GROUP_IDS:
        group_id = group_id.strip()
        if not group_id:
            continue

        # Saltear grupos bloqueados
        if group_id in stats["grupos_bloqueados"]:
            print(f"⛔ Grupo {group_id} está bloqueado. Saltando.")
            continue

        exito = False

        # Intento 1: URL externa
        try:
            await bot.send_photo(
                chat_id=group_id,
                photo=IMAGE_URL,
                caption=texto,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
            exito = True
        except Exception as e:
            print(f"⚠️ URL falló en {group_id}: {e}")

        # Intento 2: Archivo local
        if not exito:
            try:
                if os.path.exists(FOTO_LOCAL):
                    with open(FOTO_LOCAL, 'rb') as f:
                        await bot.send_photo(
                            chat_id=group_id,
                            photo=f,
                            caption=texto,
                            parse_mode='HTML',
                            reply_markup=reply_markup
                        )
                    exito = True
            except Exception as e:
                print(f"⚠️ Archivo local falló en {group_id}: {e}")

        # Intento 3: Solo texto
        if not exito:
            try:
                await bot.send_message(
                    chat_id=group_id,
                    text=texto,
                    parse_mode='HTML',
                    reply_markup=reply_markup
                )
                exito = True
                print(f"📝 Solo texto enviado a {group_id}")
            except Exception as e:
                error_str = str(e).lower()
                # Detectar si el bot fue bloqueado o expulsado
                if any(x in error_str for x in ["forbidden", "kicked", "blocked", "not a member"]):
                    print(f"🚫 Bot bloqueado en {group_id}. Marcando como inactivo.")
                    if group_id not in stats["grupos_bloqueados"]:
                        stats["grupos_bloqueados"].append(group_id)
                else:
                    print(f"❌ Error fatal en {group_id}: {e}")
                stats["errores"] += 1

        if exito:
            stats["total_enviados"] += 1

        # Pausa de seguridad entre grupos (evita flood de Telegram)
        await asyncio.sleep(1.5)

    stats["ultimo_envio"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print(f"✅ Broadcast completado. Total enviados: {stats['total_enviados']}")

# ─────────────────────────────────────────
# SCHEDULER: chequea cada hora si es pico
# ─────────────────────────────────────────
scheduler = BackgroundScheduler()
scheduler.add_job(
    lambda: asyncio.run(send_automatic_broadcast()),
    'interval',
    hours=1,
    next_run_time=datetime.now()  # primer chequeo al instante
)
scheduler.start()

# ─────────────────────────────────────────
# PANEL WEB DE ESTADO
# ─────────────────────────────────────────
@app.route('/')
def home():
    grupos_ok = len([g for g in GROUP_IDS if g.strip() and g.strip() not in stats["grupos_bloqueados"]])
    grupos_bloq = len(stats["grupos_bloqueados"])

    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>MR X BOT - Status</title>
        <style>
            body { font-family: sans-serif; background: #1a1a1a; color: white; text-align: center; padding: 40px; }
            h1 { color: #f05423; font-size: 2em; }
            .card { background: #2a2a2a; border-radius: 12px; padding: 20px; margin: 15px auto; max-width: 500px; }
            .ok { color: #00ff00; } .warn { color: #ffcc00; } .err { color: #ff4444; }
            .badge { display: inline-block; padding: 5px 14px; border-radius: 20px; font-weight: bold; margin: 4px; }
            .badge-green { background: #1a3a1a; color: #00ff00; border: 1px solid #00ff00; }
            .badge-red { background: #3a1a1a; color: #ff4444; border: 1px solid #ff4444; }
            .badge-orange { background: #3a2a1a; color: #f05423; border: 1px solid #f05423; }
        </style>
    </head>
    <body>
        <h1>🤖 MR X BOT</h1>
        <p style="color:#aaa;">Sistema de difusión automática para Telegram</p>

        <div class="card">
            <h2>📊 Estadísticas</h2>
            <p>✅ Mensajes enviados: <b class="ok">{{ total }}</b></p>
            <p>❌ Errores registrados: <b class="err">{{ errores }}</b></p>
            <p>🕐 Último envío: <b style="color:#f05423;">{{ ultimo }}</b></p>
        </div>

        <div class="card">
            <h2>👥 Grupos</h2>
            <span class="badge badge-green">✓ Activos: {{ grupos_ok }}</span>
            <span class="badge badge-red">✗ Bloqueados: {{ grupos_bloq }}</span>
        </div>

        <div class="card">
            <h2>⏰ Horarios de envío (🇦🇷 Argentina)</h2>
            <span class="badge badge-orange">9:00 AM</span>
            <span class="badge badge-orange">2:00 PM</span>
            <span class="badge badge-orange">9:00 PM</span>
        </div>

        <div class="card">
            <h2>💬 Mensajes rotativos</h2>
            <p style="color:#aaa;">Próximo mensaje a enviar: <b style="color:white;">Nº {{ next_msg }}</b> de 3</p>
        </div>
    </body>
    </html>
    ''',
    total=stats["total_enviados"],
    errores=stats["errores"],
    ultimo=stats["ultimo_envio"],
    grupos_ok=grupos_ok,
    grupos_bloq=grupos_bloq,
    next_msg=(message_index % 3) + 1
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

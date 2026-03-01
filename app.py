import os
import asyncio
import random
from datetime import datetime
from flask import Flask, render_template_string, jsonify
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from apscheduler.schedulers.background import BackgroundScheduler
from telethon import TelegramClient
from telethon.tl.types import MessageMediaDocument, MessageMediaPhoto, DocumentAttributeFilename

app = Flask(__name__)

# ─────────────────────────────────────────
# VARIABLES DE ENTORNO (Railway)
# ─────────────────────────────────────────
TOKEN      = os.getenv("TELEGRAM_TOKEN")
GROUP_IDS  = [g.strip() for g in os.getenv("GROUP_IDS", "").split(",") if g.strip()]
API_ID     = int(os.getenv("API_ID", "0"))
API_HASH   = os.getenv("API_HASH", "")
SESSION    = os.getenv("SESSION_NAME", "mrx_session")

IMAGE_URL  = "https://i.postimg.cc/qM9D8fC9/mr-x-3d-banner.jpg"
FOTO_LOCAL = "banner.jpg"
PEAK_HOURS_UTC = [12, 17, 0]

stats = {
    "total_enviados": 0,
    "reposts": 0,
    "errores": 0,
    "ultimo_envio": "Nunca",
    "grupos_bloqueados": []
}

message_index = 0

MENSAJES = [
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

def get_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Calculadora de Costos PRO",          url="https://tools.kmorra3d.com/calculadora-3d.html")],
        [InlineKeyboardButton("🌈 Calculadora AMS / Multicolor",       url="https://tools.kmorra3d.com/calculadora-ams.html")],
        [InlineKeyboardButton("🛡️ Proteger mis Diseños (Watermark)",  url="https://tools.kmorra3d.com/stl-watermark.html")],
        [InlineKeyboardButton("🤖 IA: Diagnóstico de Fallas",          url="https://tools.kmorra3d.com/diagnostico_fallos.html")],
        [InlineKeyboardButton("🎓 Academia Kmorra: Aprender a Diseñar",url="https://www.academiakmorra.com")]
    ])

# ─────────────────────────────────────────
# HELPERS: detectar tipo de archivo
# ─────────────────────────────────────────
EXTENSIONES_ARCHIVO = (".stl", ".rar", ".zip", ".7z")

def es_archivo_3d(msg):
    """Detecta STL, RAR, ZIP, 7z."""
    if not msg.media or not isinstance(msg.media, MessageMediaDocument):
        return False
    for attr in msg.media.document.attributes:
        if isinstance(attr, DocumentAttributeFilename):
            if attr.file_name.lower().endswith(EXTENSIONES_ARCHIVO):
                return True
    return False

def es_imagen(msg):
    return bool(msg.media and isinstance(msg.media, MessageMediaPhoto))

def es_contenido(msg):
    return es_imagen(msg) or es_archivo_3d(msg)

# ─────────────────────────────────────────
# CORE: armar bloques (imagen(s) + archivo)
# en orden cronológico del historial
# ─────────────────────────────────────────
def armar_bloques(mensajes):
    """
    Recorre los mensajes en orden cronológico y agrupa:
    - Una o más imágenes seguidas de un archivo = un bloque
    - Un archivo solo = bloque
    - Una imagen sola = bloque
    Devuelve lista de listas de mensajes.
    """
    # Los mensajes de Telethon vienen de más nuevo a más viejo → invertir
    mensajes_ord = list(reversed(mensajes))
    
    bloques = []
    bloque_actual = []

    for msg in mensajes_ord:
        if not es_contenido(msg):
            # Si hay bloque acumulado, cerrarlo
            if bloque_actual:
                bloques.append(bloque_actual)
                bloque_actual = []
            continue

        if es_imagen(msg):
            # Si el bloque actual ya tiene un archivo, cerrar y empezar nuevo
            if bloque_actual and es_archivo_3d(bloque_actual[-1]):
                bloques.append(bloque_actual)
                bloque_actual = []
            bloque_actual.append(msg)

        elif es_archivo_3d(msg):
            bloque_actual.append(msg)
            bloques.append(bloque_actual)
            bloque_actual = []

    # Cerrar bloque pendiente
    if bloque_actual:
        bloques.append(bloque_actual)

    return bloques

# ─────────────────────────────────────────
# REPOSTEAR + PROMO
# ─────────────────────────────────────────
async def repost_and_broadcast(group_id: str):
    global message_index
    bot = Bot(token=TOKEN)

    try:
        async with TelegramClient(SESSION, API_ID, API_HASH) as client:
            print(f"📥 Obteniendo historial de {group_id}...")
            all_messages = await client.get_messages(int(group_id), limit=2000)

            bloques = armar_bloques(all_messages)
            print(f"   → {len(bloques)} bloques encontrados")

            if not bloques:
                print(f"⚠️ Sin contenido en {group_id}")
                return

            # Elegir hasta 20 bloques al azar
            seleccionados = random.sample(bloques, min(20, len(bloques)))

            for bloque in seleccionados:
                for msg in bloque:
                    try:
                        await client.send_file(
                            int(group_id),
                            msg.media,
                            caption=""
                        )
                    except Exception as e:
                        print(f"⚠️ Error reposteando mensaje: {e}")
                stats["reposts"] += 1

            print(f"✅ {len(seleccionados)} bloques reposteados en {group_id}")

    except Exception as e:
        print(f"❌ Error Telethon en {group_id}: {e}")
        stats["errores"] += 1
        return

    # ── Mensaje promo al final ──
    texto        = MENSAJES[message_index % len(MENSAJES)]
    reply_markup = get_keyboard()
    exito        = False

    for intento in ["url", "local", "texto"]:
        try:
            if intento == "url":
                await bot.send_photo(chat_id=group_id, photo=IMAGE_URL,
                                     caption=texto, parse_mode='HTML', reply_markup=reply_markup)
            elif intento == "local" and os.path.exists(FOTO_LOCAL):
                with open(FOTO_LOCAL, 'rb') as f:
                    await bot.send_photo(chat_id=group_id, photo=f,
                                         caption=texto, parse_mode='HTML', reply_markup=reply_markup)
            else:
                await bot.send_message(chat_id=group_id, text=texto,
                                       parse_mode='HTML', reply_markup=reply_markup)
            exito = True
            break
        except Exception as e:
            err = str(e).lower()
            if any(x in err for x in ["forbidden", "kicked", "blocked", "not a member"]):
                if group_id not in stats["grupos_bloqueados"]:
                    stats["grupos_bloqueados"].append(group_id)
                stats["errores"] += 1
                return
            print(f"⚠️ Intento {intento} falló en {group_id}: {e}")

    if exito:
        stats["total_enviados"] += 1

# ─────────────────────────────────────────
# BROADCAST PRINCIPAL
# ─────────────────────────────────────────
async def send_automatic_broadcast():
    global message_index
    if not TOKEN or not GROUP_IDS:
        return

    hora_utc = datetime.utcnow().hour
    if hora_utc not in PEAK_HOURS_UTC:
        print(f"⏰ Hora UTC {hora_utc} no es pico. Saltando.")
        return

    print(f"🚀 Broadcast iniciado...")
    for group_id in GROUP_IDS:
        if group_id in stats["grupos_bloqueados"]:
            continue
        await repost_and_broadcast(group_id)
        await asyncio.sleep(2)

    message_index += 1
    stats["ultimo_envio"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

# ─────────────────────────────────────────
# SCHEDULER
# ─────────────────────────────────────────
scheduler = BackgroundScheduler()
scheduler.add_job(
    lambda: asyncio.run(send_automatic_broadcast()),
    'interval', hours=1,
    next_run_time=datetime.now()
)
scheduler.start()

# ─────────────────────────────────────────
# PANEL WEB
# ─────────────────────────────────────────
@app.route('/')
def home():
    grupos_ok   = len([g for g in GROUP_IDS if g not in stats["grupos_bloqueados"]])
    grupos_bloq = len(stats["grupos_bloqueados"])
    return render_template_string('''
    <!DOCTYPE html><html><head><meta charset="UTF-8"><title>MR X BOT</title>
    <style>
        body{font-family:sans-serif;background:#1a1a1a;color:white;text-align:center;padding:40px;}
        h1{color:#f05423;} .card{background:#2a2a2a;border-radius:12px;padding:20px;margin:15px auto;max-width:520px;}
        .ok{color:#00ff00;} .err{color:#ff4444;}
        .badge{display:inline-block;padding:5px 14px;border-radius:20px;font-weight:bold;margin:4px;}
        .bg{background:#1a3a1a;color:#00ff00;border:1px solid #00ff00;}
        .br{background:#3a1a1a;color:#ff4444;border:1px solid #ff4444;}
        .bo{background:#3a2a1a;color:#f05423;border:1px solid #f05423;}
        .btn{display:inline-block;margin-top:15px;padding:12px 30px;background:#f05423;color:white;
             border-radius:8px;text-decoration:none;font-weight:bold;font-size:1.1em;}
        .btn:hover{background:#d04010;}
    </style></head><body>
        <h1>🤖 MR X BOT</h1>
        <p style="color:#aaa">Sistema de difusión con reposts históricos</p>

        <div class="card">
            <h2>📊 Estadísticas</h2>
            <p>✅ Promos enviadas: <b class="ok">{{ total }}</b></p>
            <p>📦 Bloques reposteados: <b class="ok">{{ reposts }}</b></p>
            <p>❌ Errores: <b class="err">{{ errores }}</b></p>
            <p>🕐 Último envío: <b style="color:#f05423">{{ ultimo }}</b></p>
        </div>

        <div class="card">
            <h2>👥 Grupos</h2>
            <span class="badge bg">✓ Activos: {{ grupos_ok }}</span>
            <span class="badge br">✗ Bloqueados: {{ grupos_bloq }}</span>
        </div>

        <div class="card">
            <h2>⏰ Horarios (🇦🇷 Argentina)</h2>
            <span class="badge bo">9:00 AM</span>
            <span class="badge bo">2:00 PM</span>
            <span class="badge bo">9:00 PM</span>
        </div>

        <div class="card">
            <h2>🧪 Prueba manual</h2>
            <p style="color:#aaa;font-size:.9em">Dispara el broadcast ahora sin esperar el horario pico</p>
            <a href="/test" class="btn">▶ Ejecutar ahora</a>
        </div>
    </body></html>
    ''',
    total=stats["total_enviados"],
    reposts=stats["reposts"],
    errores=stats["errores"],
    ultimo=stats["ultimo_envio"],
    grupos_ok=grupos_ok,
    grupos_bloq=grupos_bloq
    )

# ─────────────────────────────────────────
# ENDPOINT DE PRUEBA MANUAL
# ─────────────────────────────────────────
@app.route('/test')
def test_broadcast():
    async def run():
        global message_index
        for group_id in GROUP_IDS:
            if group_id in stats["grupos_bloqueados"]:
                continue
            await repost_and_broadcast(group_id)
            await asyncio.sleep(2)
        message_index += 1
        stats["ultimo_envio"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    asyncio.run(run())
    return render_template_string('''
    <!DOCTYPE html><html><head><meta charset="UTF-8"><title>MR X BOT - Test</title>
    <style>
        body{font-family:sans-serif;background:#1a1a1a;color:white;text-align:center;padding:60px;}
        h1{color:#00ff00;} .btn{display:inline-block;margin-top:20px;padding:12px 30px;
        background:#f05423;color:white;border-radius:8px;text-decoration:none;font-weight:bold;}
    </style></head><body>
        <h1>✅ Broadcast ejecutado!</h1>
        <p style="color:#aaa">Revisá el grupo para ver los reposts y el mensaje promo.</p>
        <a href="/" class="btn">← Volver al panel</a>
    </body></html>
    ''')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

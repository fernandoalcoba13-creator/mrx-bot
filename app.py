import os
import asyncio
import random
from datetime import datetime
from flask import Flask, render_template_string
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from apscheduler.schedulers.background import BackgroundScheduler
from telethon import TelegramClient
from telethon.tl.types import MessageMediaDocument, MessageMediaPhoto, DocumentAttributeFilename

app = Flask(__name__)

# ─────────────────────────────────────────
# CONFIGURACIÓN DE VARIABLES (Railway)
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

def es_stl(msg):
    if not msg.media or not isinstance(msg.media, MessageMediaDocument):
        return False
    for attr in msg.media.document.attributes:
        if isinstance(attr, DocumentAttributeFilename) and attr.file_name.lower().endswith(".stl"):
            return True
    return False

def es_imagen(msg):
    return bool(msg.media and isinstance(msg.media, MessageMediaPhoto))

async def repost_and_broadcast(group_id: str):
    global message_index
    bot = Bot(token=TOKEN)

    try:
        async with TelegramClient(SESSION, API_ID, API_HASH) as client:
            print(f"📥 Obteniendo historial de {group_id}...")
            all_messages = await client.get_messages(int(group_id), limit=2000)

            stl_msgs   = [m for m in all_messages if es_stl(m)]
            image_msgs = [m for m in all_messages if es_imagen(m)]
            image_by_id = {m.id: m for m in image_msgs}

            print(f"   → {len(stl_msgs)} STLs | {len(image_msgs)} imágenes")

            pares  = []
            usados = set()

            for stl in stl_msgs:
                if stl.id in usados:
                    continue
                pareja = None
                for delta in range(-3, 4):
                    cid = stl.id + delta
                    if cid in image_by_id and cid not in usados:
                        pareja = image_by_id[cid]
                        break
                if pareja:
                    pares.append((pareja, stl))
                    usados.add(stl.id)
                    usados.add(pareja.id)
                else:
                    pares.append((None, stl))
                    usados.add(stl.id)

            for img in image_msgs:
                if img.id not in usados:
                    pares.append((img, None))

            if not pares:
                print(f"⚠️ Sin contenido en {group_id}")
                return

            seleccionados = random.sample(pares, min(20, len(pares)))

            for imagen_msg, stl_msg in seleccionados:
                try:
                    if imagen_msg:
                        await client.send_file(
                            int(group_id), imagen_msg.media,
                            caption="🖼️ <b>Render</b>", parse_mode="html"
                        )
                    if stl_msg:
                        await client.send_file(
                            int(group_id), stl_msg.media,
                            caption="📦 <b>Archivo STL</b>", parse_mode="html"
                        )
                    stats["reposts"] += 1
                except Exception as e:
                    print(f"⚠️ Error reposteando: {e}")

            print(f"✅ {len(seleccionados)} items reposteados en {group_id}")

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

async def send_automatic_broadcast():
    global message_index
    if not TOKEN or not GROUP_IDS:
        print("❌ Faltan variables de entorno")
        return

    hora_utc = datetime.utcnow().hour
    if hora_utc not in PEAK_HOURS_UTC:
        print(f"⏰ Hora UTC {hora_utc} no es pico. Saltando.")
        return

    print(f"🚀 Broadcast iniciado en {len(GROUP_IDS)} grupos...")
    for group_id in GROUP_IDS:
        if group_id in stats["grupos_bloqueados"]:
            continue
        await repost_and_broadcast(group_id)
        await asyncio.sleep(2)

    message_index += 1
    stats["ultimo_envio"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print(f"✅ Listo. Enviados: {stats['total_enviados']} | Reposts: {stats['reposts']}")

scheduler = BackgroundScheduler()
scheduler.add_job(
    lambda: asyncio.run(send_automatic_broadcast()),
    'interval', hours=1,
    next_run_time=datetime.now()
)
scheduler.start()

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
    </style></head><body>
        <h1>🤖 MR X BOT</h1>
        <p style="color:#aaa">Sistema de difusión con reposts históricos</p>
        <div class="card"><h2>📊 Estadísticas</h2>
            <p>✅ Promos enviadas: <b class="ok">{{ total }}</b></p>
            <p>📦 Archivos reposteados: <b class="ok">{{ reposts }}</b></p>
            <p>❌ Errores: <b class="err">{{ errores }}</b></p>
            <p>🕐 Último envío: <b style="color:#f05423">{{ ultimo }}</b></p>
        </div>
        <div class="card"><h2>👥 Grupos</h2>
            <span class="badge bg">✓ Activos: {{ grupos_ok }}</span>
            <span class="badge br">✗ Bloqueados: {{ grupos_bloq }}</span>
        </div>
        <div class="card"><h2>⏰ Horarios (🇦🇷 Argentina)</h2>
            <span class="badge bo">9:00 AM</span>
            <span class="badge bo">2:00 PM</span>
            <span class="badge bo">9:00 PM</span>
        </div>
        <div class="card"><h2>🔄 Flujo por grupo</h2>
            <p style="color:#aaa;font-size:.9em">
                📥 Lee historial → 🎲 Elige 20 al azar<br>
                📤 Repostea imagen + STL → 🚀 Envía promo final
            </p>
        </div>
    </body></html>
    ''', total=stats["total_enviados"], reposts=stats["reposts"],
         errores=stats["errores"], ultimo=stats["ultimo_envio"],
         grupos_ok=grupos_ok, grupos_bloq=grupos_bloq)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

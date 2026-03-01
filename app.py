import os
import asyncio
import random
import re
from datetime import datetime
from flask import Flask, render_template_string, jsonify
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update, ChatPermissions
from telegram.ext import Application, MessageHandler, ChatMemberHandler, filters, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler
from telethon import TelegramClient
from telethon.tl.types import MessageMediaDocument, MessageMediaPhoto, DocumentAttributeFilename
import threading

app = Flask(__name__)

# ─────────────────────────────────────────
# VARIABLES DE ENTORNO (Railway)
# ─────────────────────────────────────────
TOKEN      = os.getenv("TELEGRAM_TOKEN")
GROUP_IDS  = [g.strip() for g in os.getenv("GROUP_IDS", "").split(",") if g.strip()]
API_ID     = int(os.getenv("API_ID", "0"))
API_HASH   = os.getenv("API_HASH", "")
SESSION    = os.getenv("SESSION_NAME", "mrx_session")
STATS_GROUP = int(os.getenv("STATS_GROUP_ID", "0"))

IMAGE_URL  = "https://i.postimg.cc/qM9D8fC9/mr-x-3d-banner.jpg"
FOTO_LOCAL = "banner.jpg"
PEAK_HOURS_UTC = [12, 17, 0]

# ─────────────────────────────────────────
# RANGOS UNICODE DE IDIOMAS BLOQUEADOS
# ─────────────────────────────────────────
IDIOMAS_BLOQUEADOS = {
    "chino":   r'[\u4e00-\u9fff\u3400-\u4dbf]',
    "arabe":   r'[\u0600-\u06ff\u0750-\u077f]',
    "ruso":    r'[\u0400-\u04ff]',
    "coreano": r'[\uac00-\ud7af\u1100-\u11ff]',
}
PATRON_BLOQUEADO = re.compile("|".join(IDIOMAS_BLOQUEADOS.values()))

stats = {
    "total_enviados": 0,
    "reposts": 0,
    "errores": 0,
    "ultimo_envio": "Nunca",
    "grupos_bloqueados": [],
    "grupos": {}
}

captcha_pendiente = {}
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

def init_group_stats(group_id: str, nombre: str = ""):
    if group_id not in stats["grupos"]:
        stats["grupos"][group_id] = {
            "nombre": nombre or group_id,
            "nuevos_semana": 0,
            "spam_eliminado": 0,
            "bots_baneados": 0,
            "idioma_kick": 0,
        }
    elif nombre:
        stats["grupos"][group_id]["nombre"] = nombre

# ─────────────────────────────────────────
# HANDLER: NUEVO MIEMBRO + CAPTCHA
# ─────────────────────────────────────────
async def nuevo_miembro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.chat_member:
        return
    new_member = update.chat_member.new_chat_member
    old_member = update.chat_member.old_chat_member
    chat = update.effective_chat
    group_id = str(chat.id)

    from telegram.constants import ChatMemberStatus
    if new_member.status not in [ChatMemberStatus.MEMBER, ChatMemberStatus.RESTRICTED]:
        return
    if old_member.status not in [ChatMemberStatus.LEFT, ChatMemberStatus.BANNED]:
        return

    user = new_member.user

    # Banear bots automáticamente
    if user.is_bot:
        try:
            await context.bot.ban_chat_member(chat.id, user.id)
            init_group_stats(group_id, chat.title)
            stats["grupos"][group_id]["bots_baneados"] += 1
        except Exception as e:
            print(f"Error baneando bot: {e}")
        return

    init_group_stats(group_id, chat.title)
    stats["grupos"][group_id]["nuevos_semana"] += 1

    # Restringir hasta pasar captcha
    try:
        await context.bot.restrict_chat_member(
            chat.id, user.id,
            permissions=ChatPermissions(can_send_messages=False)
        )
    except Exception as e:
        print(f"Error restringiendo: {e}")

    num1 = random.randint(1, 9)
    num2 = random.randint(1, 9)
    respuesta = num1 + num2
    nombre = user.first_name or "nuevo miembro"

    texto = (
        f"👋 <b>¡Bienvenido/a {nombre}!</b>\n\n"
        f"🎉 Sos parte de <b>{chat.title}</b>.\n"
        f"Encontrarás STLs, renders y herramientas gratuitas para makers.\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🔐 <b>Verificación anti-bot:</b>\n"
        f"¿Cuánto es <b>{num1} + {num2}</b>?\n"
        f"Respondé con el número. Tenés 2 minutos."
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Calculadora de Costos", url="https://tools.kmorra3d.com/calculadora-3d.html")],
        [InlineKeyboardButton("🤖 IA: Diagnóstico de Fallas", url="https://tools.kmorra3d.com/diagnostico_fallos.html")],
    ])

    try:
        msg = await context.bot.send_photo(
            chat_id=chat.id, photo=IMAGE_URL,
            caption=texto, parse_mode='HTML', reply_markup=keyboard
        )
        captcha_pendiente[user.id] = {
            "group_id": chat.id, "answer": respuesta,
            "msg_id": msg.message_id, "user_name": nombre
        }
        context.job_queue.run_once(
            kick_sin_captcha, 120,
            data={"user_id": user.id, "chat_id": chat.id, "msg_id": msg.message_id},
            name=f"captcha_{user.id}"
        )
    except Exception as e:
        print(f"Error bienvenida: {e}")

async def kick_sin_captcha(context: ContextTypes.DEFAULT_TYPE):
    data = context.job.data
    user_id = data["user_id"]
    if user_id not in captcha_pendiente:
        return
    try:
        await context.bot.ban_chat_member(data["chat_id"], user_id)
        await asyncio.sleep(3)
        await context.bot.unban_chat_member(data["chat_id"], user_id)
        try:
            await context.bot.delete_message(data["chat_id"], data["msg_id"])
        except:
            pass
    except Exception as e:
        print(f"Error kick captcha: {e}")
    captcha_pendiente.pop(user_id, None)

# ─────────────────────────────────────────
# HANDLER: MENSAJES (captcha + anti-spam + idioma)
# ─────────────────────────────────────────
async def filtrar_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg  = update.message
    user = update.effective_user
    chat = update.effective_chat

    if not msg or not user:
        return

    group_id = str(chat.id)

    # No aplicar a admins
    try:
        member = await context.bot.get_chat_member(chat.id, user.id)
        from telegram.constants import ChatMemberStatus
        es_admin = member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except:
        es_admin = False

    # ── 1. Verificar captcha pendiente ──
    if user.id in captcha_pendiente and msg.text:
        datos = captcha_pendiente[user.id]
        try:
            if int(msg.text.strip()) == datos["answer"]:
                await context.bot.restrict_chat_member(
                    datos["group_id"], user.id,
                    permissions=ChatPermissions(
                        can_send_messages=True,
                        can_send_media_messages=True,
                        can_send_other_messages=True,
                        can_add_web_page_previews=True
                    )
                )
                await context.bot.send_message(
                    chat_id=datos["group_id"],
                    text=f"✅ <b>{datos['user_name']}</b> verificado/a. ¡Bienvenido/a! 🎉",
                    parse_mode='HTML'
                )
                await msg.delete()
                captcha_pendiente.pop(user.id, None)
                return
            else:
                await msg.delete()
                return
        except:
            await msg.delete()
            return

    if es_admin:
        return

    texto = msg.text or msg.caption or ""

    # ── 2. Detección de idiomas bloqueados ──
    if PATRON_BLOQUEADO.search(texto):
        try:
            await msg.delete()
            init_group_stats(group_id, chat.title)
            stats["grupos"][group_id]["idioma_kick"] += 1
            aviso = await context.bot.send_message(
                chat_id=chat.id,
                text=f"🌐 Solo se permite español, inglés y portugués en este grupo.\n"
                     f"@{user.username or user.first_name} fue removido.",
                parse_mode='HTML'
            )
            await context.bot.ban_chat_member(chat.id, user.id)
            await asyncio.sleep(3)
            await context.bot.unban_chat_member(chat.id, user.id)
            await asyncio.sleep(8)
            try:
                await aviso.delete()
            except:
                pass
        except Exception as e:
            print(f"Error kick idioma: {e}")
        return

    # ── 3. Anti-spam: links externos ──
    tiene_link = (
        "http://" in texto or "https://" in texto or
        "t.me/" in texto or "telegram.me/" in texto or
        (msg.entities and any(e.type in ["url", "text_link"] for e in msg.entities))
    )

    if tiene_link:
        try:
            await msg.delete()
            init_group_stats(group_id, chat.title)
            stats["grupos"][group_id]["spam_eliminado"] += 1
            aviso = await context.bot.send_message(
                chat_id=chat.id,
                text=f"🚫 <b>{user.first_name}</b>, los links externos no están permitidos.",
                parse_mode='HTML'
            )
            await asyncio.sleep(10)
            await aviso.delete()
        except Exception as e:
            print(f"Error anti-spam: {e}")

# ─────────────────────────────────────────
# RESUMEN SEMANAL
# ─────────────────────────────────────────
async def enviar_resumen_semanal():
    if not TOKEN or not STATS_GROUP:
        return
    bot = Bot(token=TOKEN)
    now = datetime.now().strftime("%d/%m/%Y")
    texto = f"📊 <b>RESUMEN SEMANAL MR X BOT</b>\n━━━━━━━━━━━━━━━━━━━━━━\n📅 {now}\n\n"
    texto += f"📤 Promos: <b>{stats['total_enviados']}</b>\n"
    texto += f"📦 Reposts: <b>{stats['reposts']}</b>\n\n"
    if stats["grupos"]:
        texto += "👥 <b>POR GRUPO:</b>\n"
        for gid, data in stats["grupos"].items():
            texto += (
                f"\n<b>{data.get('nombre', gid)}</b>\n"
                f"  • Nuevos: {data['nuevos_semana']}\n"
                f"  • Spam eliminado: {data['spam_eliminado']}\n"
                f"  • Bots baneados: {data['bots_baneados']}\n"
                f"  • Kicks por idioma: {data['idioma_kick']}\n"
            )
            data["nuevos_semana"] = 0
    try:
        await bot.send_message(chat_id=STATS_GROUP, text=texto, parse_mode='HTML')
    except Exception as e:
        print(f"Error resumen: {e}")

# ─────────────────────────────────────────
# HELPERS TELETHON
# ─────────────────────────────────────────
EXTENSIONES_ARCHIVO = (".stl", ".rar", ".zip", ".7z")

def es_archivo_3d(msg):
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

def armar_bloques(mensajes):
    """
    Solo devuelve bloques COMPLETOS: al menos una imagen + al menos un archivo.
    Descarta imagenes sueltas y archivos sueltos.
    """
    mensajes_ord = list(reversed(mensajes))
    bloques = []
    bloque_actual = []

    def bloque_completo(b):
        return any(es_imagen(m) for m in b) and any(es_archivo_3d(m) for m in b)

    for msg in mensajes_ord:
        if not es_contenido(msg):
            if bloque_actual:
                if bloque_completo(bloque_actual):
                    bloques.append(bloque_actual)
                bloque_actual = []
            continue

        if es_imagen(msg):
            if bloque_actual and es_archivo_3d(bloque_actual[-1]):
                if bloque_completo(bloque_actual):
                    bloques.append(bloque_actual)
                bloque_actual = []
            bloque_actual.append(msg)

        elif es_archivo_3d(msg):
            bloque_actual.append(msg)
            if bloque_completo(bloque_actual):
                bloques.append(bloque_actual)
            bloque_actual = []

    if bloque_actual and bloque_completo(bloque_actual):
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
            print(f"   → {len(bloques)} bloques")

            if not bloques:
                print(f"⚠️ Sin contenido en {group_id}")
                return

            seleccionados = random.sample(bloques, min(20, len(bloques)))
            for bloque in seleccionados:
                for msg in bloque:
                    try:
                        await client.send_file(int(group_id), msg.media, caption="")
                    except Exception as e:
                        print(f"⚠️ Error reposteando: {e}")
                stats["reposts"] += 1

    except Exception as e:
        print(f"❌ Error Telethon en {group_id}: {e}")
        stats["errores"] += 1
        return

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
        print(f"⏰ UTC {hora_utc} no es pico.")
        return
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
    'interval', hours=1, next_run_time=datetime.now()
)
scheduler.add_job(
    lambda: asyncio.run(enviar_resumen_semanal()),
    'cron', day_of_week='mon', hour=12, minute=0
)
scheduler.start()

# ─────────────────────────────────────────
# BOT TELEGRAM (handlers)
# ─────────────────────────────────────────
def run_telegram_bot():
    from telegram.ext import ApplicationBuilder
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(ChatMemberHandler(nuevo_miembro, ChatMemberHandler.CHAT_MEMBER))
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, filtrar_mensaje))
    application.run_polling(drop_pending_updates=True)

bot_thread = threading.Thread(target=run_telegram_bot, daemon=True)
bot_thread.start()

# ─────────────────────────────────────────
# PANEL WEB
# ─────────────────────────────────────────
@app.route('/')
def home():
    grupos_ok   = len([g for g in GROUP_IDS if g not in stats["grupos_bloqueados"]])
    grupos_bloq = len(stats["grupos_bloqueados"])
    grupos_html = ""
    for gid, data in stats["grupos"].items():
        grupos_html += f"""
        <div class="card" style="text-align:left">
            <h3 style="color:#f05423;margin:0 0 10px">{data.get('nombre', gid)}</h3>
            <p>👥 Nuevos esta semana: <b class="ok">{data['nuevos_semana']}</b></p>
            <p>🚫 Spam eliminado: <b class="err">{data['spam_eliminado']}</b></p>
            <p>🤖 Bots baneados: <b class="err">{data['bots_baneados']}</b></p>
            <p>🌐 Kicks por idioma: <b class="err">{data['idioma_kick']}</b></p>
        </div>"""

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
        .btn{display:inline-block;margin-top:15px;padding:12px 30px;background:#f05423;
             color:white;border-radius:8px;text-decoration:none;font-weight:bold;font-size:1.1em;}
    </style></head><body>
        <h1>🤖 MR X BOT</h1>
        <p style="color:#aaa">Sistema completo de gestión de comunidades 3D</p>

        <div class="card"><h2>📊 Estadísticas globales</h2>
            <p>✅ Promos enviadas: <b class="ok">{{ total }}</b></p>
            <p>📦 Bloques reposteados: <b class="ok">{{ reposts }}</b></p>
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

        <div class="card"><h2>🛡️ Protección activa</h2>
            <p>✅ Anti-spam (links externos)</p>
            <p>✅ Ban automático de bots</p>
            <p>✅ Captcha para nuevos miembros</p>
            <p>✅ Kick por idiomas: 🇨🇳 🇸🇦 🇷🇺 🇰🇷</p>
        </div>

        {{ grupos_html | safe }}

        <div class="card"><h2>🧪 Prueba manual</h2>
            <p style="color:#aaa;font-size:.9em">Dispara el broadcast ahora sin esperar horario pico</p>
            <a href="/test" class="btn">▶ Ejecutar ahora</a>
        </div>
    </body></html>
    ''',
    total=stats["total_enviados"], reposts=stats["reposts"],
    errores=stats["errores"], ultimo=stats["ultimo_envio"],
    grupos_ok=grupos_ok, grupos_bloq=grupos_bloq, grupos_html=grupos_html)

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
    <!DOCTYPE html><html><head><meta charset="UTF-8"><title>Test OK</title>
    <style>body{font-family:sans-serif;background:#1a1a1a;color:white;text-align:center;padding:60px;}
    h1{color:#00ff00;}.btn{display:inline-block;margin-top:20px;padding:12px 30px;
    background:#f05423;color:white;border-radius:8px;text-decoration:none;font-weight:bold;}</style>
    </head><body>
        <h1>✅ Broadcast ejecutado!</h1>
        <p style="color:#aaa">Revisá el grupo para ver los reposts y el mensaje promo.</p>
        <a href="/" class="btn">← Volver al panel</a>
    </body></html>''')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

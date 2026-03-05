import express from "express";
import helmet from "helmet";
import cors from "cors";
import morgan from "morgan";
import { config } from "../utils/config.js";
import { getStat } from "../storage/db.js";
import { promoKeyboard, promoMessage } from "../bot/promo.js";
import { repostAndPromo } from "../bot/repost.js";

export function startHttp() {
  const app = express();

  app.set("trust proxy", 1);
  app.use(morgan("combined"));
  app.use(helmet({ contentSecurityPolicy: false }));
  app.use(express.json({ limit: "200kb" }));
  app.use(cors({ origin: config.appOrigin === "*" ? true : config.appOrigin, credentials: true }));

  app.get("/health", (_req, res) => res.json({ ok: true }));

  app.get("/test", async (_req, res) => {
    const idx = getStat<number>("message_index", 0);
    const promo = promoMessage(idx);
    const keyboard = promoKeyboard();

    for (const gid of config.groupIds) {
      await repostAndPromo(gid, promo, keyboard, config.broadcastMaxBlocksPerGroup);
      await new Promise(r => setTimeout(r, 2000));
    }

    res.send("<h1>✅ Broadcast ejecutado</h1><p>Revisá tus grupos.</p><a href='/'>Volver</a>");
  });

  app.get("/", (_req, res) => {
    const total = getStat<number>("promos_sent", 0);
    const reposts = getStat<number>("reposts", 0);
    const errors = getStat<number>("errors", 0);
    const last = getStat<string>("last_send", "nunca");

    res.send(`
<!doctype html>
<html><head><meta charset="utf-8"><title>MRX Bot Panel</title>
<style>
body{font-family:system-ui;background:#0f0f12;color:#fff;margin:0;padding:30px}
.card{background:#1b1b22;border-radius:14px;padding:18px;margin:14px 0;box-shadow:0 10px 30px rgba(0,0,0,.25)}
.ok{color:#00ff90}.err{color:#ff4d4d}.btn{display:inline-block;padding:12px 18px;background:#f05423;color:#fff;border-radius:10px;text-decoration:none;font-weight:700}
</style></head>
<body>
  <h1>MRX Bot Panel</h1>
  <div class="card">
    <h2>📊 Estadísticas</h2>
    <p>✅ Promos enviadas: <b class="ok">${total}</b></p>
    <p>📦 Bloques reposteados: <b class="ok">${reposts}</b></p>
    <p>❌ Errores: <b class="err">${errors}</b></p>
    <p>🕐 Último envío: <b style="color:#f05423">${last}</b></p>
  </div>
  <div class="card">
    <h2>🧪 Prueba manual</h2>
    <p style="opacity:.8">Dispara broadcast ahora</p>
    <a class="btn" href="/test">▶ Ejecutar ahora</a>
  </div>
</body></html>`);
  });

  app.listen(config.port, () => {
    console.log("API listening on :" + config.port);
  });
}

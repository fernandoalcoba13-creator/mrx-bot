# MRX Bot (Node/TypeScript) — estilo app_boy.py

Incluye:
- Captcha a nuevos miembros (restricción + kick)
- Anti-spam: links externos + idiomas baneados
- Repost automático: detecta bloques (2-3 imágenes + archivo .stl/.zip/.rar/.7z) y los reposta con MTProto (GramJS)
- Mensaje promo con botones a tus tools
- Scheduler: corre cada N minutos y solo en horas pico UTC
- Panel web: / (stats) y /test (broadcast manual) + /health

## Requisitos
- Node 18+ (ideal 20)
- Bot token (BotFather)
- API_ID / API_HASH (my.telegram.org) para repost MTProto
- STRING_SESSION (se genera una vez con `npm run generate:session`)

## Instalación (VPS)
```bash
npm i
cp .env.example .env
nano .env
npm run dev
```

## Generar STRING_SESSION (una sola vez)
```bash
npm run generate:session
```

## Probar
- Web: http://TU_IP:3000/health
- Panel: http://TU_IP:3000/
- Broadcast manual: http://TU_IP:3000/test
- Telegram: /start /status /help

## 24/7 con PM2
```bash
npm i -g pm2
npm run build
pm2 start dist/main.js --name mrxbot
pm2 save
pm2 startup
```

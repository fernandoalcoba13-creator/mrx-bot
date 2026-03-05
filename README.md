# MRX Bot (API + Login + Telegram Bot)

## Requisitos
- Node 18+ (ideal 20)
- npm

## Instalación
```bash
npm i
cp .env.example .env
# Editá .env y pegá tu TELEGRAM_BOT_TOKEN
```

## Prisma (DB)
```bash
npm run prisma:generate
npm run prisma:migrate
```

## Crear Admin
```bash
ADMIN_EMAIL="admin@tudominio.com" ADMIN_PASSWORD="SuperSeguro_ClaveLarga123!" npm run create:admin
```

## Dev
```bash
npm run dev
```

## Probar
- API: GET /health
- Telegram: /start, /status, /help

### CSRF
Para POST/PUT/PATCH/DELETE: header `x-csrf: 1`

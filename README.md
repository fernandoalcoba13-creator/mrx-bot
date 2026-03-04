# MRX Bot (API + Login Seguro + Telegram Bot)

## Requisitos
- Node 18+ (ideal 20+)
- npm

## Instalación
```bash
npm i
cp .env.example .env
# Editá .env y pegá tu TELEGRAM_BOT_TOKEN
```

## Base de datos (Prisma)
```bash
npm run prisma:generate
npm run prisma:migrate
```

## Crear Admin
```bash
ADMIN_EMAIL="admin@tudominio.com" ADMIN_PASSWORD="SuperSeguro_ClaveLarga123!" npm run create:admin
```

## Levantar en dev
```bash
npm run dev
```

## Endpoints
- GET /health
- POST /auth/login   (requiere: email, password)
- POST /auth/logout
- GET /me            (requiere sesión)

### Nota CSRF
Para POST/PUT/PATCH/DELETE, mandar header:
x-csrf: 1

y en fetch: credentials: "include"

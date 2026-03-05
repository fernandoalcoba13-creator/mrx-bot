import dotenv from "dotenv";
dotenv.config();

function must(name: string): string {
  const v = process.env[name];
  if (!v) throw new Error(`Missing env: ${name}`);
  return v;
}

export const config = {
  nodeEnv: process.env.NODE_ENV ?? "development",
  port: Number(process.env.PORT ?? 3000),
  appOrigin: must("APP_ORIGIN"),

  cookieName: process.env.COOKIE_NAME ?? "mrx_session",
  cookieSecure: (process.env.COOKIE_SECURE ?? "false") === "true",
  sessionTtlDays: Number(process.env.SESSION_TTL_DAYS ?? 14),

  telegramToken: must("TELEGRAM_BOT_TOKEN")
};

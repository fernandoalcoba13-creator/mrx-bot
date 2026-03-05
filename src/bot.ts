import { Telegraf } from "telegraf";
import { config } from "./config.js";
import { prisma } from "./db.js";

export function buildBot() {
  const bot = new Telegraf(config.telegramToken);

  bot.start(async (ctx) => {
    await ctx.reply(
      "👋 Bienvenido a MRX Bot\n\n" +
      "Comandos:\n" +
      "• /status\n" +
      "• /help"
    );
  });

  bot.command("help", async (ctx) => {
    await ctx.reply("📌 /status para ver estado.\n📌 /help para ayuda.");
  });

  bot.command("status", async (ctx) => {
    const users = await prisma.user.count();
    await ctx.reply(`✅ MRX Bot online.\nUsuarios en DB: ${users}`);
  });

  bot.on("text", async (ctx) => {
    // Respuesta simple por defecto (podés cambiarla por tu IA)
    await ctx.reply("Te leí ✅. Probá /help o /status.");
  });

  bot.catch(async (err, ctx) => {
    console.error("Bot error", err);
    try { await ctx.reply("⚠️ Ocurrió un error."); } catch {}
  });

  return bot;
}

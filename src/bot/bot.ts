import { Telegraf } from "telegraf";
import { config } from "../utils/config.js";
import { getStat } from "../storage/db.js";

export function buildBot() {
  const bot = new Telegraf(config.botToken);

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
    const last = getStat<string>("last_send", "nunca");
    await ctx.reply(`✅ MRX Bot online.\nÚltimo broadcast: ${last}`);
  });

  return bot;
}

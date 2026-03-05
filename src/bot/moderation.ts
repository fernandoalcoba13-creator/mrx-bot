import { Telegraf } from "telegraf";
import { config } from "../utils/config.js";
import { hasBannedLanguage, hasExternalLink } from "../utils/textFilters.js";
import { incStat, logAudit } from "../storage/db.js";

export function installModeration(bot: Telegraf) {
  bot.on("message", async (ctx, next) => {
    const chatId = ctx.chat?.id;
    if (!chatId || !config.groupIds.includes(chatId)) return next();

    const from = ctx.from;
    const userId = from?.id;
    const text =
      // @ts-ignore
      (ctx.message?.text as string | undefined) ??
      // @ts-ignore
      (ctx.message?.caption as string | undefined) ??
      "";

    if (!text) return next();

    if (config.kickOnBannedLanguage && hasBannedLanguage(text)) {
      await ctx.deleteMessage().catch(() => {});
      incStat("deleted_banned_language", 1);
      logAudit("deleted_banned_language", { chatId, userId });

      if (userId) {
        await ctx.telegram.banChatMember(chatId, userId).catch(() => {});
        await ctx.telegram.unbanChatMember(chatId, userId).catch(() => {});
        incStat("kicked_banned_language", 1);
      }
      return;
    }

    if (hasExternalLink(text)) {
      await ctx.deleteMessage().catch(() => {});
      incStat("deleted_links", 1);
      logAudit("deleted_link", { chatId, userId, text: text.slice(0, 120) });

      if (config.kickOnExternalLinks && userId) {
        await ctx.telegram.banChatMember(chatId, userId).catch(() => {});
        await ctx.telegram.unbanChatMember(chatId, userId).catch(() => {});
        incStat("kicked_links", 1);
      }
      return;
    }

    return next();
  });
}

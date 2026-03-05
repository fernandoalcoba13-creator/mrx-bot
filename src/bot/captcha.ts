import { Telegraf } from "telegraf";
import { config } from "../utils/config.js";
import { incStat, logAudit } from "../storage/db.js";

type Pending = {
  chatId: number;
  userId: number;
  correct: number;
  timer: NodeJS.Timeout;
};

const pending = new Map<string, Pending>();

function key(chatId: number, userId: number) {
  return `${chatId}:${userId}`;
}

function randInt(min: number, max: number) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

export function installCaptcha(bot: Telegraf) {
  bot.on("new_chat_members", async (ctx) => {
    const chatId = ctx.chat.id;
    if (!config.groupIds.includes(chatId)) return;

    for (const member of ctx.message.new_chat_members) {
      const userId = member.id;

      const a = randInt(1, 9);
      const b = randInt(1, 9);
      const correct = a + b;

      try {
        await ctx.telegram.restrictChatMember(chatId, userId, {
          permissions: {
            can_send_messages: false,
            can_send_audios: false,
            can_send_documents: false,
            can_send_photos: false,
            can_send_videos: false,
            can_send_video_notes: false,
            can_send_voice_notes: false,
            can_send_polls: false,
            can_send_other_messages: false,
            can_add_web_page_previews: false,
            can_change_info: false,
            can_invite_users: false,
            can_pin_messages: false,
            can_manage_topics: false
          }
        });
      } catch (e) {
        console.error("restrict error:", e);
      }

      const msg = await ctx.reply(
        `🛡️ Verificación anti-spam\n\n` +
        `👤 ${member.first_name ?? "nuevo"}: resolvé esto para hablar:\n` +
        `👉 ${a} + ${b} = ?\n\n` +
        `⏳ Tenés ${config.captchaTimeoutSec}s. Si no, te saco automáticamente.`
      );

      incStat("captcha_shown", 1);
      logAudit("captcha_shown", { chatId, userId });

      const timer = setTimeout(async () => {
        const k = key(chatId, userId);
        if (!pending.has(k)) return;

        pending.delete(k);
        try {
          await ctx.telegram.banChatMember(chatId, userId);
          await ctx.telegram.unbanChatMember(chatId, userId);
          await ctx.telegram.deleteMessage(chatId, msg.message_id).catch(() => {});
        } catch {}
        incStat("captcha_failed", 1);
        logAudit("captcha_failed_kick", { chatId, userId });
      }, config.captchaTimeoutSec * 1000);

      pending.set(key(chatId, userId), { chatId, userId, correct, timer });
    }
  });

  bot.on("text", async (ctx, next) => {
    const chatId = ctx.chat.id;
    const userId = ctx.from?.id;
    if (!userId) return next();

    const k = key(chatId, userId);
    const p = pending.get(k);
    if (!p) return next();

    const text = ctx.message.text.trim();
    const n = Number(text);
    if (!Number.isFinite(n)) {
      await ctx.deleteMessage().catch(() => {});
      return;
    }

    if (n === p.correct) {
      clearTimeout(p.timer);
      pending.delete(k);

      try {
        await ctx.telegram.restrictChatMember(chatId, userId, {
          permissions: {
            can_send_messages: true,
            can_send_audios: true,
            can_send_documents: true,
            can_send_photos: true,
            can_send_videos: true,
            can_send_video_notes: true,
            can_send_voice_notes: true,
            can_send_polls: true,
            can_send_other_messages: true,
            can_add_web_page_previews: true,
            can_change_info: false,
            can_invite_users: true,
            can_pin_messages: false,
            can_manage_topics: false
          }
        });
      } catch {}

      await ctx.reply("✅ Verificado. ¡Bienvenido!");
      incStat("captcha_passed", 1);
      logAudit("captcha_passed", { chatId, userId });
      await ctx.deleteMessage().catch(() => {});
      return;
    }

    await ctx.deleteMessage().catch(() => {});
  });
}

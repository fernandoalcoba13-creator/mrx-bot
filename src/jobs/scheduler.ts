import cron from "node-cron";
import { config } from "../utils/config.js";
import { promoKeyboard, promoMessage } from "../bot/promo.js";
import { repostAndPromo } from "../bot/repost.js";
import { setStat, getStat, logAudit } from "../storage/db.js";

function utcHour() {
  return new Date().getUTCHours();
}

export function startScheduler() {
  const every = Math.max(1, config.broadcastIntervalMinutes);
  const expr = `*/${every} * * * *`;

  cron.schedule(expr, async () => {
    const h = utcHour();
    if (config.peakHoursUtc.length && !config.peakHoursUtc.includes(h)) return;

    let msgIndex = getStat<number>("message_index", 0);
    const promo = promoMessage(msgIndex);
    const keyboard = promoKeyboard();

    for (const gid of config.groupIds) {
      await repostAndPromo(gid, promo, keyboard, config.broadcastMaxBlocksPerGroup);
      await new Promise(r => setTimeout(r, 2000));
    }

    msgIndex += 1;
    setStat("message_index", msgIndex);
    setStat("last_send", new Date().toISOString());
    logAudit("auto_broadcast", { hourUtc: h });
  });

  cron.schedule("0 12 * * 1", async () => {
    setStat("last_weekly", new Date().toISOString());
    logAudit("weekly_summary", {});
  });

  console.log("Scheduler started:", expr, "peakHoursUtc=", config.peakHoursUtc.join(","));
}

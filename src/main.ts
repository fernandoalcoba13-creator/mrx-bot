import { buildBot } from "./bot/bot.js";
import { installCaptcha } from "./bot/captcha.js";
import { installModeration } from "./bot/moderation.js";
import { startHttp } from "./http/server.js";
import { startScheduler } from "./jobs/scheduler.js";

async function main() {
  startHttp();

  const bot = buildBot();
  installCaptcha(bot);
  installModeration(bot);

  await bot.launch();
  console.log("Telegram bot launched");

  startScheduler();

  process.once("SIGINT", () => bot.stop("SIGINT"));
  process.once("SIGTERM", () => bot.stop("SIGTERM"));
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});

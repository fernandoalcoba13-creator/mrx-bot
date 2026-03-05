import dotenv from "dotenv";
dotenv.config();

const must = (k: string) => {
  const v = process.env[k];
  if (!v) throw new Error(`Missing env: ${k}`);
  return v;
};

const csv = (s: string | undefined) =>
  (s ?? "").split(",").map(x => x.trim()).filter(Boolean);

export const config = {
  nodeEnv: process.env.NODE_ENV ?? "development",
  port: Number(process.env.PORT ?? 3000),
  appOrigin: process.env.APP_ORIGIN ?? "*",

  botToken: must("TELEGRAM_BOT_TOKEN"),
  groupIds: csv(process.env.GROUP_IDS).map(x => Number(x)),
  statsChatId: process.env.STATS_CHAT_ID ? Number(process.env.STATS_CHAT_ID) : undefined,

  kickOnBannedLanguage: (process.env.KICK_ON_BANNED_LANGUAGE ?? "true") === "true",
  kickOnExternalLinks: (process.env.KICK_ON_EXTERNAL_LINKS ?? "false") === "true",

  captchaTimeoutSec: Number(process.env.CAPTCHA_TIMEOUT_SEC ?? 120),

  peakHoursUtc: csv(process.env.PEAK_HOURS_UTC).map(x => Number(x)).filter(n => !Number.isNaN(n)),
  broadcastIntervalMinutes: Number(process.env.BROADCAST_INTERVAL_MINUTES ?? 60),
  broadcastMaxBlocksPerGroup: Number(process.env.BROADCAST_MAX_BLOCKS_PER_GROUP ?? 20),

  apiId: Number(must("API_ID")),
  apiHash: must("API_HASH"),
  stringSession: must("STRING_SESSION"),

  links: {
    stlMarker: process.env.TOOLS_STL_MARKER ?? "https://tools.kmorra3d.com/",
    costs: process.env.TOOLS_COSTS ?? "https://tools.kmorra3d.com/",
    ams: process.env.TOOLS_AMS ?? "https://tools.kmorra3d.com/",
    ai: process.env.TOOLS_AI ?? "https://tools.kmorra3d.com/"
  }
};

import { TelegramClient } from "telegram";
import { StringSession } from "telegram/sessions/index.js";
import { config } from "../utils/config.js";
import { loadTracking, saveTracking } from "../storage/tracking.js";
import { incStat, logAudit } from "../storage/db.js";
import path from "node:path";

const allowedExt = new Set([".stl", ".zip", ".rar", ".7z"]);

function isImage(m: any) {
  return Boolean(m?.media?.photo);
}

function is3DFile(m: any) {
  const doc = m?.media?.document;
  if (!doc) return false;
  const attrs = doc.attributes ?? [];
  const fileNameAttr = attrs.find((a: any) => a?.className === "DocumentAttributeFilename");
  const name = fileNameAttr?.fileName as string | undefined;
  if (!name) return false;
  const ext = path.extname(name).toLowerCase();
  return allowedExt.has(ext);
}

function buildBlocks(messages: any[]) {
  const blocks: any[][] = [];
  const msgs = messages.slice().sort((a, b) => (a.id ?? 0) - (b.id ?? 0));

  let i = 0;
  while (i < msgs.length) {
    if (!isImage(msgs[i])) { i++; continue; }

    const images: any[] = [msgs[i]];
    let j = i + 1;
    while (j < msgs.length && images.length < 3 && isImage(msgs[j])) {
      images.push(msgs[j]);
      j++;
    }

    if (images.length < 2) { i++; continue; }

    let fileMsg: any | null = null;
    let k = j;
    while (k < msgs.length && k <= j + 2) {
      if (is3DFile(msgs[k])) { fileMsg = msgs[k]; break; }
      k++;
    }

    if (fileMsg) {
      blocks.push([...images, fileMsg]);
      i = k + 1;
    } else {
      i += images.length;
    }
  }
  return blocks;
}

let client: TelegramClient | null = null;

export async function getClient() {
  if (client) return client;
  const session = new StringSession(config.stringSession);
  client = new TelegramClient(session, config.apiId, config.apiHash, { connectionRetries: 5 });
  await client.start({});
  return client;
}

export async function repostAndPromo(chatId: number, promoHtml: string, keyboard: any, maxBlocks: number) {
  const c = await getClient();

  const messages = await c.getMessages(chatId, { limit: 2000 });
  const blocks = buildBlocks(messages as any[]);

  if (!blocks.length) {
    logAudit("repost_no_blocks", { chatId });
    return;
  }

  const tracking = loadTracking();
  const key = String(chatId);
  const used = new Set<number>(tracking[key] ?? []);

  const fresh = blocks.filter(b => !used.has(b[0].id));
  const pool = fresh.length ? fresh : blocks;
  if (!fresh.length) used.clear();

  const selected = pool.slice(0, Math.min(maxBlocks, pool.length));

  for (const block of selected) {
    for (const m of block) {
      try {
        // @ts-ignore
        await c.sendFile(chatId, { file: m.media, caption: "" });
      } catch (e) {
        console.error("sendFile error:", e);
        incStat("errors", 1);
      }
    }
    used.add(block[0].id);
    incStat("reposts", 1);
  }

  tracking[key] = Array.from(used).slice(-5000);
  saveTracking(tracking);

  await c.sendMessage(chatId, {
    message: promoHtml,
    parseMode: "html",
    buttons: keyboard.inline_keyboard
  }).catch((e: any) => {
    console.error("promo error:", e);
    incStat("errors", 1);
  });

  incStat("promos_sent", 1);
  logAudit("broadcast_done", { chatId, blocks: selected.length });
}

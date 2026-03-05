import Database from "better-sqlite3";
import fs from "node:fs";
import path from "node:path";

const dataDir = path.resolve(process.cwd(), "data");
if (!fs.existsSync(dataDir)) fs.mkdirSync(dataDir, { recursive: true });

export const db = new Database(path.join(dataDir, "mrx.db"));
db.pragma("journal_mode = WAL");

db.exec(`
CREATE TABLE IF NOT EXISTS stats (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS audit (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts INTEGER NOT NULL,
  action TEXT NOT NULL,
  meta TEXT
);
`);

export function getStat<T>(key: string, fallback: T): T {
  const row = db.prepare("SELECT value FROM stats WHERE key=?").get(key) as any;
  if (!row) return fallback;
  try { return JSON.parse(row.value) as T; } catch { return fallback; }
}

export function setStat(key: string, value: unknown) {
  const v = JSON.stringify(value);
  db.prepare("INSERT INTO stats(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value").run(key, v);
}

export function incStat(key: string, by = 1) {
  const cur = getStat<number>(key, 0);
  setStat(key, cur + by);
}

export function logAudit(action: string, meta?: any) {
  db.prepare("INSERT INTO audit(ts, action, meta) VALUES(?,?,?)")
    .run(Date.now(), action, meta ? JSON.stringify(meta) : null);
}

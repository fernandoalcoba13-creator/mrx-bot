import fs from "node:fs";
import path from "node:path";

const dataDir = path.resolve(process.cwd(), "data");
const file = path.join(dataDir, "tracking.json");

type Tracking = Record<string, number[]>;

export function loadTracking(): Tracking {
  try {
    const raw = fs.readFileSync(file, "utf8");
    const parsed = JSON.parse(raw) as Tracking;
    return parsed ?? {};
  } catch {
    return {};
  }
}

export function saveTracking(t: Tracking) {
  fs.writeFileSync(file, JSON.stringify(t, null, 2), "utf8");
}

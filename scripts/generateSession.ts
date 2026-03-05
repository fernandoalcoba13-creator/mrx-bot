import input from "input";
import { TelegramClient } from "telegram";
import { StringSession } from "telegram/sessions/index.js";
import dotenv from "dotenv";
dotenv.config();

const apiId = Number(process.env.API_ID);
const apiHash = process.env.API_HASH;

if (!apiId || !apiHash) {
  console.error("Set API_ID and API_HASH in your environment first.");
  process.exit(1);
}

(async () => {
  console.log("Generating STRING_SESSION (GramJS) ...");
  const session = new StringSession("");
  const client = new TelegramClient(session, apiId, apiHash, { connectionRetries: 5 });

  await client.start({
    phoneNumber: async () => await input.text("Phone (international, +54...): "),
    password: async () => await input.password("2FA Password (if any): "),
    phoneCode: async () => await input.text("Code (Telegram): "),
    onError: (err) => console.log(err)
  });

  const s = client.session.save();
  console.log("\n✅ STRING_SESSION (copy to .env):\n");
  console.log(s);
  await client.disconnect();
})();

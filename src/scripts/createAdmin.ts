import argon2 from "argon2";
import { prisma } from "../db.js";

const email = process.env.ADMIN_EMAIL ?? "admin@mrx.local";
const password = process.env.ADMIN_PASSWORD ?? "ChangeMe_12345678";

const run = async () => {
  const passwordHash = await argon2.hash(password, { type: argon2.argon2id });

  const user = await prisma.user.upsert({
    where: { email },
    update: { passwordHash, role: "ADMIN", isActive: true },
    create: { email, passwordHash, role: "ADMIN" }
  });

  console.log("Admin ready:", { id: user.id, email: user.email, role: user.role });
};

run()
  .catch((e) => { console.error(e); process.exit(1); })
  .finally(async () => { await prisma.$disconnect(); });

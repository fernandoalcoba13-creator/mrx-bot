import { Router } from "express";
import { z } from "zod";
import argon2 from "argon2";
import { prisma } from "../db.js";
import { config } from "../config.js";
import { authLimiter } from "../security/rateLimit.js";
import { validateBody } from "../security/validate.js";
import { createSession } from "../security/auth.js";

export const authRouter = Router();

const LoginSchema = z.object({
  email: z.string().email().min(3).max(200),
  password: z.string().min(8).max(200)
});

authRouter.post(
  "/login",
  authLimiter,
  validateBody(LoginSchema),
  async (req, res) => {
    const { email, password } = req.body as z.infer<typeof LoginSchema>;

    const user = await prisma.user.findUnique({ where: { email } });
    const ip = req.ip;
    const userAgent = req.get("user-agent") ?? undefined;

    const audit = async (action: string, meta?: string, userId?: string) => {
      await prisma.auditLog.create({
        data: { action, meta, userId, ip, userAgent }
      });
    };

    if (!user || !user.isActive) {
      await audit("LOGIN_FAILED", "user_not_found_or_inactive");
      return res.status(401).json({ error: "INVALID_CREDENTIALS" });
    }

    const ok = await argon2.verify(user.passwordHash, password).catch(() => false);
    if (!ok) {
      await audit("LOGIN_FAILED", "wrong_password", user.id);
      return res.status(401).json({ error: "INVALID_CREDENTIALS" });
    }

    const session = await createSession({ userId: user.id, ip, userAgent });
    await audit("LOGIN_SUCCESS", undefined, user.id);

    res.cookie(config.cookieName, session.id, {
      httpOnly: true,
      secure: config.cookieSecure,
      sameSite: "lax",
      path: "/",
      expires: session.expiresAt
    });

    return res.json({ ok: true });
  }
);

authRouter.post("/logout", async (req, res) => {
  const sid = req.cookies?.[config.cookieName];
  if (sid) {
    await prisma.session.delete({ where: { id: sid } }).catch(() => {});
  }
  res.clearCookie(config.cookieName, { path: "/" });
  return res.json({ ok: true });
});

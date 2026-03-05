import type { RequestHandler } from "express";
import { nanoid } from "nanoid";
import { prisma } from "../db.js";
import { config } from "../config.js";

type Role = "ADMIN" | "USER";

declare global {
  namespace Express {
    interface Request {
      user?: { id: string; role: Role; email: string };
      sessionId?: string;
    }
  }
}

export async function createSession(params: {
  userId: string;
  ip?: string;
  userAgent?: string;
}) {
  const id = nanoid(32);
  const now = new Date();
  const expiresAt = new Date(now.getTime() + config.sessionTtlDays * 24 * 60 * 60 * 1000);

  await prisma.session.create({
    data: {
      id,
      userId: params.userId,
      expiresAt,
      ip: params.ip,
      userAgent: params.userAgent
    }
  });

  return { id, expiresAt };
}

export const attachUserFromSession: RequestHandler = async (req, _res, next) => {
  const sid = req.cookies?.[config.cookieName];
  if (!sid) return next();

  const session = await prisma.session.findUnique({
    where: { id: sid },
    include: { user: true }
  });

  if (!session) return next();

  if (session.expiresAt.getTime() < Date.now()) {
    await prisma.session.delete({ where: { id: sid } }).catch(() => {});
    return next();
  }

  if (!session.user.isActive) return next();

  const role = (session.user.role === "ADMIN" ? "ADMIN" : "USER") as Role;

  req.sessionId = session.id;
  req.user = { id: session.user.id, role, email: session.user.email };
  next();
};

export const requireAuth: RequestHandler = (req, res, next) => {
  if (!req.user) return res.status(401).json({ error: "UNAUTHORIZED" });
  next();
};

export function requireRole(role: Role): RequestHandler {
  return (req, res, next) => {
    if (!req.user) return res.status(401).json({ error: "UNAUTHORIZED" });
    if (req.user.role !== role) return res.status(403).json({ error: "FORBIDDEN" });
    next();
  };
}

import type { RequestHandler } from "express";

const MUTATING = new Set(["POST", "PUT", "PATCH", "DELETE"]);

export const requireCsrfHeader: RequestHandler = (req, res, next) => {
  if (!MUTATING.has(req.method)) return next();
  const v = req.header("x-csrf");
  if (v !== "1") return res.status(403).json({ error: "CSRF_REQUIRED" });
  next();
};

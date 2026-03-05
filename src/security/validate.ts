import type { RequestHandler } from "express";
import type { ZodSchema } from "zod";

export function validateBody(schema: ZodSchema): RequestHandler {
  return (req, res, next) => {
    const parsed = schema.safeParse(req.body);
    if (!parsed.success) {
      return res.status(400).json({
        error: "VALIDATION_ERROR",
        issues: parsed.error.issues.map(i => ({ path: i.path, message: i.message }))
      });
    }
    req.body = parsed.data;
    next();
  };
}

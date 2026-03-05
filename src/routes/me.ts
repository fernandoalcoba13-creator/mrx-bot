import { Router } from "express";
import { requireAuth } from "../security/auth.js";

export const meRouter = Router();

meRouter.get("/", requireAuth, async (req, res) => {
  res.json({ user: req.user });
});

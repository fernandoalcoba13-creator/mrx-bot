import express from "express";
import helmet from "helmet";
import cors from "cors";
import cookieParser from "cookie-parser";
import morgan from "morgan";
import { config } from "./config.js";
import { generalLimiter } from "./security/rateLimit.js";
import { requireCsrfHeader } from "./security/csrf.js";
import { attachUserFromSession } from "./security/auth.js";
import { authRouter } from "./routes/auth.js";
import { meRouter } from "./routes/me.js";
import { healthRouter } from "./routes/health.js";
import { buildBot } from "./bot.js";

const app = express();

app.set("trust proxy", 1);

app.use(morgan("combined"));
app.use(helmet({ contentSecurityPolicy: false }));
app.use(express.json({ limit: "200kb" }));
app.use(cookieParser());

app.use(cors({
  origin: config.appOrigin,
  credentials: true,
  methods: ["GET","POST","PUT","PATCH","DELETE"]
}));

app.use(generalLimiter);
app.use(attachUserFromSession);
app.use(requireCsrfHeader);

app.use("/health", healthRouter);
app.use("/auth", authRouter);
app.use("/me", meRouter);

app.listen(config.port, () => {
  console.log(`API listening on :${config.port}`);
});

const bot = buildBot();
bot.launch().then(() => console.log("Telegram bot launched"));

process.once("SIGINT", () => bot.stop("SIGINT"));
process.once("SIGTERM", () => bot.stop("SIGTERM"));

import { httpRouter } from "convex/server";
import { httpAction } from "./_generated/server";
import { internal } from "./_generated/api";
import { SUCCESS_MESSAGE } from "./constants";
import {
  cleanSource,
  isHoneypotFilled,
  isOriginAllowed,
  isTruthyFlag,
  isValidEmail,
  looksLikeToken,
  normalizeEmail,
  parseOrigins,
  randomToken,
  renderPage,
} from "./lib";

const http = httpRouter();

// ---------- CORS ----------

function corsHeaders(req: Request): Record<string, string> | null {
  const origin = req.headers.get("Origin");
  if (origin === null) return {}; // not a browser cross-origin request (curl, server)
  const ok = isOriginAllowed(
    origin,
    parseOrigins(process.env.ALLOWED_ORIGINS),
    isTruthyFlag(process.env.ALLOW_DEV_ORIGINS),
  );
  if (!ok) return null;
  return {
    "Access-Control-Allow-Origin": origin,
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Max-Age": "86400",
    Vary: "Origin",
  };
}

function json(body: unknown, status: number, extra: Record<string, string> = {}) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json", "Cache-Control": "no-store", ...extra },
  });
}

function html(body: string, status = 200) {
  return new Response(body, {
    status,
    headers: {
      "Content-Type": "text/html; charset=utf-8",
      "Cache-Control": "no-store",
      "Referrer-Policy": "no-referrer",
      "X-Robots-Tag": "noindex",
    },
  });
}

async function ipKey(req: Request): Promise<string> {
  const ip =
    req.headers.get("cf-connecting-ip") ??
    req.headers.get("x-real-ip") ??
    req.headers.get("x-forwarded-for")?.split(",")[0]?.trim() ??
    "unknown";
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(ip));
  return [...new Uint8Array(digest).slice(0, 12)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

// ---------- /subscribe ----------

http.route({
  path: "/subscribe",
  method: "OPTIONS",
  handler: httpAction(async (_ctx, req) => {
    const cors = corsHeaders(req);
    if (!cors) return new Response(null, { status: 403 });
    return new Response(null, { status: 204, headers: cors });
  }),
});

http.route({
  path: "/subscribe",
  method: "POST",
  handler: httpAction(async (ctx, req) => {
    const cors = corsHeaders(req);
    if (!cors) return json({ ok: false, message: "Origin not allowed." }, 403);

    let body: Record<string, unknown>;
    try {
      const text = await req.text();
      if (text.length > 4096) return json({ ok: false, message: "Request too large." }, 413, cors);
      const ct = req.headers.get("Content-Type") ?? "";
      body = ct.includes("application/x-www-form-urlencoded")
        ? Object.fromEntries(new URLSearchParams(text))
        : JSON.parse(text);
      if (!body || typeof body !== "object") throw new Error("not an object");
    } catch {
      return json({ ok: false, message: "Could not read the request." }, 400, cors);
    }

    // Honeypot: look successful, store nothing.
    if (isHoneypotFilled(body.website)) return json({ ok: true, message: SUCCESS_MESSAGE }, 200, cors);

    const email = normalizeEmail(body.email);
    if (!isValidEmail(email)) {
      return json({ ok: false, message: "Please enter a valid email address." }, 400, cors);
    }

    const result = await ctx.runMutation(internal.subscribers.subscribe, {
      email,
      source: cleanSource(body.source),
      token: randomToken(),
      ipKey: await ipKey(req),
    });
    if (result === "limited") {
      return json({ ok: false, message: "Too many requests. Please try again later." }, 429, {
        ...cors,
        "Retry-After": "600",
      });
    }
    return json({ ok: true, message: SUCCESS_MESSAGE }, 200, cors);
  }),
});

// ---------- /confirm ----------

http.route({
  path: "/confirm",
  method: "GET",
  handler: httpAction(async (ctx, req) => {
    const site = process.env.SITE_URL || undefined;
    const token = new URL(req.url).searchParams.get("token");
    if (!looksLikeToken(token)) {
      return html(renderPage("Link not valid", "This confirmation link is not valid. Try signing up again.", site), 400);
    }
    const r = await ctx.runMutation(internal.subscribers.confirm, { token });
    switch (r) {
      case "confirmed":
      case "already":
        return html(renderPage("You're subscribed", "Thanks for confirming. We will write when a result lands.", site));
      case "unsubscribed":
        return html(renderPage("You unsubscribed", "This address was unsubscribed. Sign up again on the site if you want updates.", site));
      default:
        return html(renderPage("Link not valid", "This confirmation link is not valid. Try signing up again.", site), 404);
    }
  }),
});

// ---------- /unsubscribe (GET from a link, POST for one-click RFC 8058) ----------

const unsubscribeHandler = httpAction(async (ctx, req) => {
  const site = process.env.SITE_URL || undefined;
  const token = new URL(req.url).searchParams.get("token");
  if (!looksLikeToken(token)) {
    return html(renderPage("Link not valid", "This unsubscribe link is not valid.", site), 400);
  }
  const r = await ctx.runMutation(internal.subscribers.unsubscribe, { token });
  if (r === "invalid") return html(renderPage("Link not valid", "This unsubscribe link is not valid.", site), 404);
  return html(renderPage("You're unsubscribed", "You will not get any more emails from us.", site));
});

http.route({ path: "/unsubscribe", method: "GET", handler: unsubscribeHandler });
http.route({ path: "/unsubscribe", method: "POST", handler: unsubscribeHandler });

export default http;

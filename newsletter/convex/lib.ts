// Pure helpers (no Convex APIs) so they can be unit-tested directly.
import { EMAIL_SUBJECT, GOAL_LINE, GROUP_NAME, RESEND_PENDING_AFTER_MS, WHAT_YOU_GET } from "./constants";

export type Status = "pending" | "confirmed" | "unsubscribed";

// ---------- validation ----------

export function normalizeEmail(raw: unknown): string {
  return typeof raw === "string" ? raw.trim().toLowerCase() : "";
}

// Deliberately simple: one @, a dot in the domain, no spaces, sane lengths.
const EMAIL_RE = /^[a-z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?(?:\.[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)+$/;

export function isValidEmail(email: string): boolean {
  if (email.length < 6 || email.length > 254) return false;
  const [local] = email.split("@");
  if (!local || local.length > 64) return false;
  if (email.includes("..")) return false;
  return EMAIL_RE.test(email);
}

/** The "website" field is hidden from people; bots fill it. */
export function isHoneypotFilled(website: unknown): boolean {
  return typeof website === "string" ? website.trim().length > 0 : website != null && website !== false;
}

export function cleanSource(raw: unknown): string {
  if (typeof raw !== "string") return "";
  return raw.trim().slice(0, 200);
}

// ---------- state transitions ----------

export type SubscribeDecision =
  | { kind: "insert"; send: true }
  | { kind: "noop"; send: false } // already confirmed, or pending and emailed within the hour
  | { kind: "resend"; send: true } // pending, last email over an hour ago
  | { kind: "reactivate"; send: true }; // unsubscribed -> pending

export function decideSubscribe(
  existing: { status: Status; lastEmailAt?: number } | null,
  now: number,
): SubscribeDecision {
  if (!existing) return { kind: "insert", send: true };
  switch (existing.status) {
    case "confirmed":
      return { kind: "noop", send: false };
    case "pending":
      if (existing.lastEmailAt !== undefined && now - existing.lastEmailAt < RESEND_PENDING_AFTER_MS) {
        return { kind: "noop", send: false };
      }
      return { kind: "resend", send: true };
    case "unsubscribed":
      return { kind: "reactivate", send: true };
  }
}

export type ConfirmDecision = "confirm" | "already" | "unsubscribed";
export function decideConfirm(status: Status): ConfirmDecision {
  if (status === "pending") return "confirm";
  if (status === "confirmed") return "already";
  return "unsubscribed"; // an old confirm link must not re-subscribe someone who left
}

export function decideUnsubscribe(status: Status): "unsubscribe" | "already" {
  return status === "unsubscribed" ? "already" : "unsubscribe";
}

// ---------- rate limiting (fixed window) ----------

export function windowStart(now: number, windowMs: number): number {
  return now - (now % windowMs);
}

// ---------- CORS ----------

export function parseOrigins(raw: string | undefined): string[] {
  return (raw ?? "")
    .split(",")
    .map((s) => s.trim().replace(/\/+$/, ""))
    .filter(Boolean);
}

export function isTruthyFlag(v: string | undefined): boolean {
  return !!v && ["1", "true", "yes", "on"].includes(v.trim().toLowerCase());
}

const DEV_ORIGIN_RE = /^http:\/\/(localhost|127\.0\.0\.1|\[::1\])(:\d+)?$/;

export function isOriginAllowed(origin: string, allowed: string[], allowDev: boolean): boolean {
  if (allowed.includes(origin)) return true;
  if (allowDev && (origin === "null" || DEV_ORIGIN_RE.test(origin))) return true;
  return false;
}

// ---------- HTML helpers ----------

// Attributes in this project are always double-quoted, so single quotes stay as-is.
export function escapeHtml(s: string): string {
  return s.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]!);
}

const LOGO_URL = "https://openindus.pages.dev/assets/email-logo.png";
const SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif";

export function renderPage(title: string, message: string, siteUrl?: string): string {
  const back = siteUrl
    ? `<p class="back"><a href="${escapeHtml(siteUrl)}">Back to ${escapeHtml(GROUP_NAME)}</a></p>`
    : "";
  return `<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>${escapeHtml(title)} | ${escapeHtml(GROUP_NAME)}</title>
<style>
body{margin:0;font:17px/1.55 ${SANS};color:#1f1b16;background:#e9e3d8;text-align:center}
main{max-width:30rem;margin:12vh auto;padding:40px 28px;background:#f3efe7;border-radius:14px}
img{display:block;margin:0 auto 28px;width:240px;max-width:100%;height:auto}
h1{font-size:26px;line-height:1.2;margin:0 0 12px}
p{margin:0;color:#5b5348}
.back{margin-top:28px}
a{color:#1f1b16;font-weight:600}
@media (max-width:32rem){main{margin:0;min-height:100vh;border-radius:0;box-sizing:border-box}}
</style></head>
<body><main><img src="${LOGO_URL}" width="240" height="48" alt="${escapeHtml(GROUP_NAME)}"><h1>${escapeHtml(title)}</h1><p>${escapeHtml(message)}</p>${back}</main></body></html>`;
}

// ---------- email ----------

export function buildWelcomeEmail(confirmUrl: string, unsubscribeUrl: string) {
  const subject = EMAIL_SUBJECT;
  const text = [
    "Hello,",
    "",
    `${GROUP_NAME} is ${GOAL_LINE}.`,
    "",
    `If you confirm, you will get ${WHAT_YOU_GET.charAt(0).toLowerCase()}${WHAT_YOU_GET.slice(1)}`,
    "",
    "Confirm your subscription:",
    confirmUrl,
    "",
    "If you did not ask for this, ignore this email and you will not be subscribed.",
    "",
    `Unsubscribe: ${unsubscribeUrl}`,
    "",
  ].join("\n");

  const c = escapeHtml(confirmUrl);
  const u = escapeHtml(unsubscribeUrl);
  const html = `<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light only">
<meta name="supported-color-schemes" content="light only">
<title>${escapeHtml(subject)}</title></head>
<body style="margin:0;padding:0;background:#e9e3d8;color:#1f1b16">
<div style="display:none;max-height:0;overflow:hidden">${escapeHtml(WHAT_YOU_GET)}</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#e9e3d8"><tr><td align="center" style="padding:32px 16px">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#f3efe7" style="max-width:520px;background:#f3efe7;border-radius:14px">
<tr><td align="center" style="padding:36px 32px 8px"><img src="${LOGO_URL}" width="240" height="48" alt="${escapeHtml(GROUP_NAME)}" style="display:block;border:0;width:240px;height:auto"></td></tr>
<tr><td align="center" style="padding:20px 32px 0;font:700 26px/1.25 ${SANS};color:#1f1b16">Confirm your subscription</td></tr>
<tr><td align="center" style="padding:14px 32px 0;font:17px/1.55 ${SANS};color:#3d362e">${escapeHtml(GROUP_NAME)} is ${escapeHtml(GOAL_LINE)}.</td></tr>
<tr><td align="center" style="padding:12px 32px 0;font:17px/1.55 ${SANS};color:#3d362e">If you confirm, you will get ${escapeHtml(WHAT_YOU_GET.charAt(0).toLowerCase() + WHAT_YOU_GET.slice(1))}</td></tr>
<tr><td align="center" style="padding:28px 32px 0"><a href="${c}" style="display:inline-block;padding:14px 28px;background:#1f1b16;color:#f3efe7;text-decoration:none;border-radius:8px;font:600 16px/1.2 ${SANS}">Confirm subscription</a></td></tr>
<tr><td align="center" style="padding:24px 32px 0;font:13px/1.5 ${SANS};color:#6b6358">Or paste this link into your browser:<br><a href="${c}" style="color:#6b6358;word-break:break-all">${c}</a></td></tr>
<tr><td align="center" style="padding:24px 32px 36px;font:14px/1.5 ${SANS};color:#6b6358">If you did not ask for this, ignore this email and you will not be subscribed.</td></tr>
</table>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width:520px"><tr><td align="center" style="padding:18px 32px 0;font:13px/1.5 ${SANS};color:#6b6358">${escapeHtml(GROUP_NAME)} &middot; <a href="${u}" style="color:#6b6358">Unsubscribe</a></td></tr></table>
</td></tr></table>
</body></html>`;

  const headers = {
    "List-Unsubscribe": `<${unsubscribeUrl}>`,
    "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
  };
  return { subject, text, html, headers };
}

// ---------- tokens ----------

/** 32 random bytes, base64url. Call only from actions (real randomness). */
export function randomToken(): string {
  const bytes = new Uint8Array(32);
  crypto.getRandomValues(bytes);
  let s = "";
  for (const b of bytes) s += String.fromCharCode(b);
  return btoa(s).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

export function looksLikeToken(t: unknown): t is string {
  return typeof t === "string" && /^[A-Za-z0-9_-]{40,64}$/.test(t);
}

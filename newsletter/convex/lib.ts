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

export function renderPage(title: string, message: string, siteUrl?: string): string {
  const back = siteUrl
    ? `<p><a href="${escapeHtml(siteUrl)}">Back to ${escapeHtml(GROUP_NAME)}</a></p>`
    : "";
  return `<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<meta name="robots" content="noindex">
<title>${escapeHtml(title)} | ${escapeHtml(GROUP_NAME)}</title>
<style>
body{font:17px/1.5 Georgia,serif;max-width:32rem;margin:15vh auto;padding:0 16px;color:#1b1b1b;background:#fbfaf7}
a{color:inherit}
@media (prefers-color-scheme: dark){body{color:#ece9e2;background:#151412}}
</style></head>
<body><h1>${escapeHtml(title)}</h1><p>${escapeHtml(message)}</p>${back}</body></html>`;
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
<meta name="color-scheme" content="light dark">
<meta name="supported-color-schemes" content="light dark">
<title>${escapeHtml(subject)}</title>
<style>
@media (prefers-color-scheme: dark){
  .body{background:#151412 !important;color:#ece9e2 !important}
  .btn{background:#ece9e2 !important;color:#151412 !important}
  .muted{color:#a9a49a !important}
}
</style></head>
<body class="body" style="margin:0;padding:0;background:#fbfaf7;color:#1b1b1b">
<div style="display:none;max-height:0;overflow:hidden">${escapeHtml(WHAT_YOU_GET)}</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td align="center" style="padding:32px 16px">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width:520px">
<tr><td style="font:17px/1.55 Georgia,'Times New Roman',serif">
<p style="margin:0 0 16px">Hello,</p>
<p style="margin:0 0 16px">${escapeHtml(GROUP_NAME)} is ${escapeHtml(GOAL_LINE)}.</p>
<p style="margin:0 0 24px">If you confirm, you will get ${escapeHtml(WHAT_YOU_GET.charAt(0).toLowerCase() + WHAT_YOU_GET.slice(1))}</p>
<p style="margin:0 0 24px"><a class="btn" href="${c}" style="display:inline-block;padding:12px 20px;background:#1b1b1b;color:#fbfaf7;text-decoration:none;border-radius:6px;font:600 16px/1.2 -apple-system,'Segoe UI',Helvetica,Arial,sans-serif">Confirm subscription</a></p>
<p class="muted" style="margin:0 0 16px;font-size:14px;color:#5c5850">Or paste this link into your browser:<br><a href="${c}" style="color:inherit;word-break:break-all">${c}</a></p>
<p style="margin:0 0 32px">If you did not ask for this, ignore this email and you will not be subscribed.</p>
<p class="muted" style="margin:0;font-size:13px;color:#5c5850"><a href="${u}" style="color:inherit">Unsubscribe</a></p>
</td></tr></table></td></tr></table>
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

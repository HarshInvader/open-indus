import { describe, expect, it } from "vitest";
import {
  buildWelcomeEmail,
  decideConfirm,
  decideSubscribe,
  decideUnsubscribe,
  isHoneypotFilled,
  isOriginAllowed,
  isValidEmail,
  looksLikeToken,
  normalizeEmail,
  parseOrigins,
  randomToken,
} from "../convex/lib";
import { RESEND_PENDING_AFTER_MS } from "../convex/constants";

describe("email validation", () => {
  it("normalizes case and whitespace", () => {
    expect(normalizeEmail("  Reader@Example.COM ")).toBe("reader@example.com");
    expect(normalizeEmail(42)).toBe("");
  });
  it.each(["a@example.com", "first.last+tag@sub.example.org", "x_y@ex-ample.io"])("accepts %s", (e) =>
    expect(isValidEmail(e)).toBe(true),
  );
  it.each(["", "plain", "a@b", "a@@example.com", "a b@example.com", "a..b@example.com", "a@-example.com", "@example.com", "a@example.", `${"x".repeat(65)}@example.com`])(
    "rejects %j",
    (e) => expect(isValidEmail(e)).toBe(false),
  );
});

describe("honeypot", () => {
  it("is empty for people", () => {
    expect(isHoneypotFilled("")).toBe(false);
    expect(isHoneypotFilled("   ")).toBe(false);
    expect(isHoneypotFilled(undefined)).toBe(false);
    expect(isHoneypotFilled(null)).toBe(false);
  });
  it("is filled by bots", () => {
    expect(isHoneypotFilled("http://spam.example")).toBe(true);
    expect(isHoneypotFilled(1)).toBe(true);
  });
});

describe("state transitions", () => {
  const now = 10 * RESEND_PENDING_AFTER_MS;
  it("new address -> insert + send", () => expect(decideSubscribe(null, now)).toEqual({ kind: "insert", send: true }));
  it("confirmed -> no-op, no email", () =>
    expect(decideSubscribe({ status: "confirmed", lastEmailAt: 0 }, now)).toEqual({ kind: "noop", send: false }));
  it("pending emailed within the hour -> no-op", () =>
    expect(decideSubscribe({ status: "pending", lastEmailAt: now - 1000 }, now).send).toBe(false));
  it("pending emailed over an hour ago -> resend", () =>
    expect(decideSubscribe({ status: "pending", lastEmailAt: now - RESEND_PENDING_AFTER_MS }, now)).toEqual({
      kind: "resend",
      send: true,
    }));
  it("unsubscribed -> back to pending + send", () =>
    expect(decideSubscribe({ status: "unsubscribed" }, now)).toEqual({ kind: "reactivate", send: true }));
  it("confirm only moves pending", () => {
    expect(decideConfirm("pending")).toBe("confirm");
    expect(decideConfirm("confirmed")).toBe("already");
    expect(decideConfirm("unsubscribed")).toBe("unsubscribed");
  });
  it("unsubscribe is idempotent", () => {
    expect(decideUnsubscribe("pending")).toBe("unsubscribe");
    expect(decideUnsubscribe("confirmed")).toBe("unsubscribe");
    expect(decideUnsubscribe("unsubscribed")).toBe("already");
  });
});

describe("CORS origins", () => {
  const allowed = parseOrigins(" https://open-indus.pages.dev/ , https://example.org ");
  it("parses and trims", () => expect(allowed).toEqual(["https://open-indus.pages.dev", "https://example.org"]));
  it("allows listed origins only", () => {
    expect(isOriginAllowed("https://example.org", allowed, false)).toBe(true);
    expect(isOriginAllowed("https://evil.example", allowed, false)).toBe(false);
    expect(isOriginAllowed("http://localhost:8000", allowed, false)).toBe(false);
    expect(isOriginAllowed("null", allowed, false)).toBe(false);
  });
  it("allows localhost and file:// (null) only with the dev flag", () => {
    expect(isOriginAllowed("http://localhost:8000", allowed, true)).toBe(true);
    expect(isOriginAllowed("http://127.0.0.1", allowed, true)).toBe(true);
    expect(isOriginAllowed("null", allowed, true)).toBe(true);
    expect(isOriginAllowed("http://localhost.evil.example", allowed, true)).toBe(false);
  });
});

describe("tokens and email", () => {
  it("tokens are long, url-safe and distinct", () => {
    const a = randomToken();
    expect(looksLikeToken(a)).toBe(true);
    expect(a).not.toBe(randomToken());
  });
  it("email has unsubscribe headers, both parts, no remote images, no em dashes", () => {
    const m = buildWelcomeEmail("https://x.convex.site/confirm?token=T", "https://x.convex.site/unsubscribe?token=T");
    expect(m.subject).toBe("Confirm your Open Indus subscription");
    expect(m.headers["List-Unsubscribe"]).toBe("<https://x.convex.site/unsubscribe?token=T>");
    expect(m.headers["List-Unsubscribe-Post"]).toBe("List-Unsubscribe=One-Click");
    expect(m.text).toContain("https://x.convex.site/confirm?token=T");
    expect(m.text).toContain("ignore this email");
    expect(m.html.match(/<img/gi)?.length).toBe(1); // only the logo, no tracking pixel
    expect(m.html).toContain("https://openindus.pages.dev/assets/email-logo.png");
    expect(m.text + m.html + m.subject).not.toMatch(/—/);
  });
});

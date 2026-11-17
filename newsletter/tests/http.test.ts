/// <reference types="vite/client" />
import { convexTest } from "convex-test";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import schema from "../convex/schema";
import { internal } from "../convex/_generated/api";
import { SUCCESS_MESSAGE } from "../convex/constants";

const modules = import.meta.glob("../convex/**/*.ts");

const post = (body: unknown, headers: Record<string, string> = {}) => ({
  method: "POST",
  headers: { "Content-Type": "application/json", ...headers },
  body: JSON.stringify(body),
});

beforeEach(() => {
  vi.useFakeTimers();
  vi.stubEnv("ALLOWED_ORIGINS", "https://site.example");
  vi.stubEnv("ALLOW_DEV_ORIGINS", "");
  vi.stubEnv("RESEND_API_KEY", "");
  vi.stubEnv("EMAIL_FROM", "");
});
afterEach(() => {
  vi.useRealTimers();
  vi.unstubAllEnvs();
});

async function count(t: ReturnType<typeof convexTest>) {
  return t.query(internal.subscribers.counts, {});
}

describe("POST /subscribe", () => {
  it("honeypot: answers OK and stores nothing", async () => {
    const t = convexTest(schema, modules);
    const res = await t.fetch("/subscribe", post({ email: "bot@example.com", website: "spam" }));
    expect(res.status).toBe(200);
    expect((await res.json()).message).toBe(SUCCESS_MESSAGE);
    expect((await count(t)).total).toBe(0);
  });

  it("rejects an invalid email", async () => {
    const t = convexTest(schema, modules);
    const res = await t.fetch("/subscribe", post({ email: "nope" }));
    expect(res.status).toBe(400);
  });

  it("same answer for new, pending and confirmed addresses", async () => {
    const t = convexTest(schema, modules);
    const a = await (await t.fetch("/subscribe", post({ email: " New@Example.com ", source: "/" }))).json();
    const { token } = (await t.query(internal.subscribers.tokenFor, { email: "new@example.com" }))!;
    await t.fetch(`/confirm?token=${token}`);
    const b = await (await t.fetch("/subscribe", post({ email: "new@example.com" }))).json();
    expect(a).toEqual(b);
    expect(await count(t)).toMatchObject({ confirmed: 1, total: 1 });
  });

  it("CORS: allowed origin echoed, other origin refused, dev origins need the flag", async () => {
    const t = convexTest(schema, modules);
    const ok = await t.fetch("/subscribe", { method: "OPTIONS", headers: { Origin: "https://site.example" } });
    expect(ok.status).toBe(204);
    expect(ok.headers.get("Access-Control-Allow-Origin")).toBe("https://site.example");
    const bad = await t.fetch("/subscribe", post({ email: "a@example.com" }, { Origin: "https://evil.example" }));
    expect(bad.status).toBe(403);
    expect((await count(t)).total).toBe(0);
    const devOff = await t.fetch("/subscribe", { method: "OPTIONS", headers: { Origin: "null" } });
    expect(devOff.status).toBe(403);
    vi.stubEnv("ALLOW_DEV_ORIGINS", "1");
    const devOn = await t.fetch("/subscribe", { method: "OPTIONS", headers: { Origin: "null" } });
    expect(devOn.headers.get("Access-Control-Allow-Origin")).toBe("null");
  });

  it("rate-limits per IP", async () => {
    const t = convexTest(schema, modules);
    const statuses: number[] = [];
    for (let i = 0; i < 7; i++) {
      const r = await t.fetch("/subscribe", post({ email: `r${i}@example.com` }, { "x-forwarded-for": "203.0.113.9" }));
      statuses.push(r.status);
    }
    expect(statuses).toEqual([200, 200, 200, 200, 200, 429, 429]);
  });
});

describe("full lifecycle", () => {
  it("pending -> confirmed -> unsubscribed -> pending again; email skipped while unconfigured", async () => {
    const t = convexTest(schema, modules);
    await t.fetch("/subscribe", post({ email: "life@example.com", source: "/about" }));
    await t.finishAllScheduledFunctions(vi.runAllTimers); // sendWelcome runs, logs "not configured"
    let s = (await t.query(internal.subscribers.tokenFor, { email: "life@example.com" }))!;
    expect(s.status).toBe("pending");

    const c = await t.fetch(`/confirm?token=${s.token}`);
    expect(c.status).toBe(200);
    expect(await c.text()).toContain("You're subscribed");
    expect((await t.query(internal.subscribers.exportConfirmed, {})).map((r) => r.email)).toEqual(["life@example.com"]);

    const u = await t.fetch(`/unsubscribe?token=${s.token}`, {
      method: "POST",
      body: "List-Unsubscribe=One-Click",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });
    expect(u.status).toBe(200);
    s = (await t.query(internal.subscribers.tokenFor, { email: "life@example.com" }))!;
    expect(s.status).toBe("unsubscribed");

    // An old confirm link must not re-subscribe.
    expect(await (await t.fetch(`/confirm?token=${s.token}`)).text()).toContain("You unsubscribed");

    await t.fetch("/subscribe", post({ email: "life@example.com" }));
    expect((await t.query(internal.subscribers.tokenFor, { email: "life@example.com" }))!.status).toBe("pending");

    const bad = await t.fetch("/confirm?token=" + "x".repeat(43));
    expect(bad.status).toBe(404);
  });

  it("sends through Resend when configured, with the unsubscribe headers", async () => {
    vi.stubEnv("RESEND_API_KEY", "re_test");
    vi.stubEnv("EMAIL_FROM", "Open Indus <updates@news.example>");
    vi.stubEnv("CONVEX_SITE_URL", "https://test.convex.site");
    const calls: { url: string; body: any }[] = [];
    vi.stubGlobal("fetch", async (url: string, init: RequestInit) => {
      calls.push({ url, body: JSON.parse(init.body as string) });
      return new Response(JSON.stringify({ id: "1" }), { status: 200 });
    });
    const t = convexTest(schema, modules);
    await t.fetch("/subscribe", post({ email: "send@example.com" }));
    await t.finishAllScheduledFunctions(vi.runAllTimers);
    vi.unstubAllGlobals();
    expect(calls).toHaveLength(1);
    expect(calls[0].url).toBe("https://api.resend.com/emails");
    expect(calls[0].body.to).toEqual(["send@example.com"]);
    expect(calls[0].body.headers["List-Unsubscribe-Post"]).toBe("List-Unsubscribe=One-Click");
    expect(calls[0].body.text).toMatch(/https:\/\/test\.convex\.site\/confirm\?token=/);
  });
});

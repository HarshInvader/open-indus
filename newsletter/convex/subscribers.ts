import { v } from "convex/values";
import { internalMutation, internalQuery, type MutationCtx } from "./_generated/server";
import { internal } from "./_generated/api";
import { GLOBAL_LIMIT, IP_LIMIT } from "./constants";
import { decideConfirm, decideSubscribe, decideUnsubscribe, windowStart } from "./lib";

async function hit(ctx: MutationCtx, key: string, limit: { max: number; windowMs: number }, now: number) {
  const start = windowStart(now, limit.windowMs);
  const row = await ctx.db
    .query("rateLimits")
    .withIndex("by_key_window", (q) => q.eq("key", key).eq("windowStart", start))
    .unique();
  if (row && row.count >= limit.max) return false;
  if (row) await ctx.db.patch(row._id, { count: row.count + 1 });
  else await ctx.db.insert("rateLimits", { key, windowStart: start, count: 1 });
  return true;
}

/**
 * Called by POST /subscribe after validation. Applies rate limits, upserts the
 * subscriber and schedules the welcome email. Returns only "ok" | "limited" so
 * the HTTP layer cannot leak who is subscribed.
 */
export const subscribe = internalMutation({
  args: { email: v.string(), source: v.string(), token: v.string(), ipKey: v.string() },
  returns: v.union(v.literal("ok"), v.literal("limited")),
  handler: async (ctx, { email, source, token, ipKey }) => {
    const now = Date.now();
    if (!(await hit(ctx, `ip:${ipKey}`, IP_LIMIT, now))) return "limited";
    if (!(await hit(ctx, "global", GLOBAL_LIMIT, now))) return "limited";

    const existing = await ctx.db
      .query("subscribers")
      .withIndex("by_email", (q) => q.eq("email", email))
      .unique();
    const decision = decideSubscribe(existing, now);

    let id = existing?._id;
    switch (decision.kind) {
      case "insert":
        id = await ctx.db.insert("subscribers", {
          email,
          status: "pending",
          token,
          source,
          createdAt: now,
          lastEmailAt: now,
        });
        break;
      case "resend":
        await ctx.db.patch(existing!._id, { lastEmailAt: now });
        break;
      case "reactivate":
        await ctx.db.patch(existing!._id, {
          status: "pending",
          lastEmailAt: now,
          confirmedAt: undefined,
          unsubscribedAt: undefined,
          source: source || existing!.source,
        });
        break;
      case "noop":
        break;
    }
    if (decision.send && id) {
      await ctx.scheduler.runAfter(0, internal.email.sendWelcome, { id });
    }
    return "ok";
  },
});

export const confirm = internalMutation({
  args: { token: v.string() },
  returns: v.union(v.literal("confirmed"), v.literal("already"), v.literal("unsubscribed"), v.literal("invalid")),
  handler: async (ctx, { token }) => {
    const sub = await ctx.db
      .query("subscribers")
      .withIndex("by_token", (q) => q.eq("token", token))
      .unique();
    if (!sub) return "invalid";
    const d = decideConfirm(sub.status);
    if (d === "confirm") {
      await ctx.db.patch(sub._id, { status: "confirmed", confirmedAt: Date.now() });
      return "confirmed";
    }
    return d;
  },
});

export const unsubscribe = internalMutation({
  args: { token: v.string() },
  returns: v.union(v.literal("unsubscribed"), v.literal("already"), v.literal("invalid")),
  handler: async (ctx, { token }) => {
    const sub = await ctx.db
      .query("subscribers")
      .withIndex("by_token", (q) => q.eq("token", token))
      .unique();
    if (!sub) return "invalid";
    if (decideUnsubscribe(sub.status) === "already") return "already";
    await ctx.db.patch(sub._id, { status: "unsubscribed", unsubscribedAt: Date.now() });
    return "unsubscribed";
  },
});

// ---------- used by the email action ----------

export const get = internalQuery({
  args: { id: v.id("subscribers") },
  handler: (ctx, { id }) => ctx.db.get(id),
});

export const markWelcomeSent = internalMutation({
  args: { id: v.id("subscribers") },
  handler: async (ctx, { id }) => {
    await ctx.db.patch(id, { welcomeSentAt: Date.now() });
  },
});

export const pendingWithoutWelcome = internalQuery({
  args: {},
  handler: async (ctx) => {
    const pending = await ctx.db
      .query("subscribers")
      .withIndex("by_status", (q) => q.eq("status", "pending"))
      .collect();
    return pending.filter((s) => s.welcomeSentAt === undefined).map((s) => s._id);
  },
});

// ---------- owner tools (npx convex run ...), never exposed over HTTP ----------

/** npx convex run subscribers:exportConfirmed [--prod] */
export const exportConfirmed = internalQuery({
  args: {},
  handler: async (ctx) => {
    const rows = await ctx.db
      .query("subscribers")
      .withIndex("by_status", (q) => q.eq("status", "confirmed"))
      .collect();
    return rows.map((s) => ({
      email: s.email,
      confirmedAt: s.confirmedAt ? new Date(s.confirmedAt).toISOString() : null,
      source: s.source,
    }));
  },
});

/** npx convex run subscribers:counts [--prod] */
export const counts = internalQuery({
  args: {},
  handler: async (ctx) => {
    const out = { pending: 0, confirmed: 0, unsubscribed: 0, total: 0 };
    for await (const s of ctx.db.query("subscribers")) {
      out[s.status]++;
      out.total++;
    }
    return out;
  },
});

/** Testing aid: npx convex run subscribers:tokenFor '{"email":"a@example.com"}' */
export const tokenFor = internalQuery({
  args: { email: v.string() },
  handler: async (ctx, { email }) => {
    const s = await ctx.db
      .query("subscribers")
      .withIndex("by_email", (q) => q.eq("email", email.trim().toLowerCase()))
      .unique();
    return s ? { token: s.token, status: s.status } : null;
  },
});

/** Delete on request: npx convex run subscribers:deleteByEmail '{"email":"a@example.com"}' --prod */
export const deleteByEmail = internalMutation({
  args: { email: v.string() },
  handler: async (ctx, { email }) => {
    const s = await ctx.db
      .query("subscribers")
      .withIndex("by_email", (q) => q.eq("email", email.trim().toLowerCase()))
      .unique();
    if (!s) return { deleted: false };
    await ctx.db.delete(s._id);
    return { deleted: true };
  },
});

/** Daily cleanup of old rate-limit rows (see crons.ts). */
export const pruneRateLimits = internalMutation({
  args: {},
  handler: async (ctx) => {
    const cutoff = Date.now() - 24 * 60 * 60 * 1000;
    let n = 0;
    for await (const r of ctx.db.query("rateLimits")) {
      if (r.windowStart < cutoff) {
        await ctx.db.delete(r._id);
        n++;
      }
    }
    return n;
  },
});

import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  subscribers: defineTable({
    email: v.string(), // lowercased, trimmed
    status: v.union(v.literal("pending"), v.literal("confirmed"), v.literal("unsubscribed")),
    token: v.string(), // random, unguessable; used in confirm and unsubscribe links
    source: v.string(), // page the form was on
    createdAt: v.number(),
    confirmedAt: v.optional(v.number()),
    unsubscribedAt: v.optional(v.number()),
    lastEmailAt: v.optional(v.number()), // last time a welcome was queued (throttles re-sends)
    welcomeSentAt: v.optional(v.number()), // last time Resend accepted a welcome
  })
    .index("by_email", ["email"])
    .index("by_token", ["token"])
    .index("by_status", ["status"]),

  // Fixed-window counters. Keys are "ip:<sha256 prefix>" or "global"; no raw IPs stored.
  rateLimits: defineTable({
    key: v.string(),
    windowStart: v.number(),
    count: v.number(),
  }).index("by_key_window", ["key", "windowStart"]),
});

import { v } from "convex/values";
import { internalAction, type ActionCtx } from "./_generated/server";
import { internal } from "./_generated/api";
import type { Id } from "./_generated/dataModel";
import { buildWelcomeEmail } from "./lib";

function emailConfig() {
  const apiKey = process.env.RESEND_API_KEY;
  const from = process.env.EMAIL_FROM;
  return apiKey && from ? { apiKey, from } : null;
}

/** Returns "sent" | "skipped" | "not_configured" | "failed". Never throws. */
async function send(
  ctx: ActionCtx,
  id: Id<"subscribers">,
): Promise<"sent" | "skipped" | "not_configured" | "failed"> {
  const sub = await ctx.runQuery(internal.subscribers.get, { id });
  if (!sub || sub.status !== "pending") return "skipped";

  const cfg = emailConfig();
  if (!cfg) {
    console.log("Email not configured (RESEND_API_KEY / EMAIL_FROM unset); subscriber kept as pending.");
    return "not_configured";
  }

  const base = process.env.CONVEX_SITE_URL!; // built in on every deployment
  const token = encodeURIComponent(sub.token);
  const msg = buildWelcomeEmail(`${base}/confirm?token=${token}`, `${base}/unsubscribe?token=${token}`);

  try {
    const res = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${cfg.apiKey}`,
        "Content-Type": "application/json",
        // Same subscriber + same hour -> Resend drops duplicates.
        "Idempotency-Key": `welcome-${id}-${Math.floor(Date.now() / 3_600_000)}`,
      },
      body: JSON.stringify({
        from: cfg.from,
        to: [sub.email],
        subject: msg.subject,
        text: msg.text,
        html: msg.html,
        headers: msg.headers,
        ...(process.env.EMAIL_REPLY_TO ? { reply_to: process.env.EMAIL_REPLY_TO } : {}),
      }),
    });
    if (!res.ok) {
      console.error(`Resend error ${res.status}: ${(await res.text()).slice(0, 500)}`);
      return "failed";
    }
    await ctx.runMutation(internal.subscribers.markWelcomeSent, { id });
    return "sent";
  } catch (e) {
    console.error("Resend request failed", e);
    return "failed";
  }
}

export const sendWelcome = internalAction({
  args: { id: v.id("subscribers") },
  handler: async (ctx, { id }) => {
    await send(ctx, id);
  },
});

/**
 * Run once a sender exists, to email everyone who signed up while sending was off:
 *   npx convex run email:sendPendingWelcomes --prod
 */
export const sendPendingWelcomes = internalAction({
  args: {},
  handler: async (ctx): Promise<Record<string, number | string>> => {
    if (!emailConfig()) return { error: "RESEND_API_KEY and EMAIL_FROM must both be set" };
    const ids: Id<"subscribers">[] = await ctx.runQuery(internal.subscribers.pendingWithoutWelcome, {});
    const tally: Record<string, number> = {};
    for (const id of ids) {
      const r = await send(ctx, id);
      tally[r] = (tally[r] ?? 0) + 1;
      await new Promise((r) => setTimeout(r, 600)); // stay under Resend's 2 req/s default
    }
    return { considered: ids.length, ...tally };
  },
});

import { cronJobs } from "convex/server";
import { internal } from "./_generated/api";

const crons = cronJobs();
crons.daily("prune rate limits", { hourUTC: 3, minuteUTC: 0 }, internal.subscribers.pruneRateLimits, {});
export default crons;

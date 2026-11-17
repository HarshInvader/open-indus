// Group name and goal line live here so a rename (for example to "Read Indus")
// is a one-file change. Keep copy plain: no em dashes, no hype.

export const GROUP_NAME = "Open Indus";

/** Completes the sentence "<GROUP_NAME> is ..." */
export const GOAL_LINE =
  "an open research group working to decipher the Indus script by 2027, testing every idea in public";

export const EMAIL_SUBJECT = `Confirm your ${GROUP_NAME} subscription`;

/** Shown on pages and used as the email preheader. */
export const WHAT_YOU_GET =
  "An occasional update when a result lands, positive or negative. No more than about one a month.";

export const SUCCESS_MESSAGE =
  "Thanks. Check your inbox for a confirmation email. You are not subscribed until you click the link in it.";

// Limits
export const RESEND_PENDING_AFTER_MS = 60 * 60 * 1000; // re-send to a pending address at most once per hour
export const IP_LIMIT = { max: 5, windowMs: 10 * 60 * 1000 }; // per IP: 5 requests / 10 min
export const GLOBAL_LIMIT = { max: 200, windowMs: 60 * 60 * 1000 }; // everyone: 200 requests / hour

# Open Indus newsletter backend

Double opt-in newsletter signup on Convex. One email does both jobs: it welcomes and asks to confirm. Nobody is subscribed until they click the link.

All commands below run from this folder (`indus-decipher/newsletter/`). Add `--prod` to act on production; without it they hit the dev deployment.

## What exists in Convex

Project `open-indus-newsletter` (its own project, separate from every other app in the account).

| Deployment | Functions URL (`.convex.cloud`) | HTTP URL the site calls (`.convex.site`) |
| --- | --- | --- |
| dev | https://famous-grasshopper-773.convex.cloud | https://famous-grasshopper-773.convex.site |
| production | https://hardy-capybara-487.convex.cloud | https://hardy-capybara-487.convex.site |

Tables: `subscribers` (email, status pending/confirmed/unsubscribed, token, source, createdAt, confirmedAt, unsubscribedAt, lastEmailAt, welcomeSentAt) and `rateLimits` (hashed-IP counters; no raw IPs stored, pruned daily by a cron).

## Endpoints

| Method + path | What it does |
| --- | --- |
| `POST /subscribe` `{email, source, website}` | Validates, rate-limits (5 per IP per 10 min, 200 total per hour), upserts, queues the email. Always the same success message, so it never reveals who is subscribed. A filled `website` honeypot gets the success message and nothing is stored. |
| `GET /confirm?token=...` | Marks confirmed, shows "You're subscribed" and a link back if `SITE_URL` is set. An old link does not re-subscribe someone who unsubscribed. |
| `GET /unsubscribe?token=...` | Marks unsubscribed, shows a small page. |
| `POST /unsubscribe?token=...` | Same, for one-click unsubscribe from Gmail/Apple Mail (RFC 8058, `List-Unsubscribe-Post`). |

Note: some corporate mail scanners open links in emails. That can confirm a pending address (harmless: it still proves the mailbox exists) or, rarely, follow the unsubscribe link in the footer. If unexplained unsubscribes show up, change `GET /unsubscribe` to show a button that POSTs instead.

## Environment variables

| Name | Where | Value |
| --- | --- | --- |
| `ALLOWED_ORIGINS` | both | Comma-separated site origins, no trailing slash. Production holds a placeholder now. |
| `ALLOW_DEV_ORIGINS` | dev only | `1` lets `http://localhost:*`, `http://127.0.0.1:*` and `file://` pages (origin `null`) call it. Leave unset on production. |
| `SITE_URL` | optional | Link shown on the confirm/unsubscribe pages, e.g. `https://openindus.org`. |
| `RESEND_API_KEY` | to send | Resend API key. |
| `EMAIL_FROM` | to send | e.g. `Open Indus <updates@news.your-domain>`; must be on a domain verified in Resend. |
| `EMAIL_REPLY_TO` | optional | Where replies go. |

Set, check or remove:

```sh
npx convex env set ALLOWED_ORIGINS "https://open-indus.pages.dev,https://your-domain.org" --prod
npx convex env set SITE_URL "https://open-indus.pages.dev" --prod
npx convex env list --prod
npx convex env remove ALLOW_DEV_ORIGINS
```

Env changes apply immediately; no redeploy needed. When the site moves to its own domain, keep the pages.dev origin in the list until the old address stops serving.

## Turning on the welcome email

Until both `RESEND_API_KEY` and `EMAIL_FROM` are set, signups are stored as pending and the log says "Email not configured". Nothing fails.

1. Create a Resend account, add a sending domain (a subdomain like `news.your-domain.org` keeps the main domain's reputation separate), add the DNS records Resend shows (SPF, DKIM; add a DMARC record too), wait for "Verified".
2. Create an API key with "Sending access" only.
3. Set both on production:
   ```sh
   npx convex env set RESEND_API_KEY "re_..." --prod
   npx convex env set EMAIL_FROM "Open Indus <updates@news.your-domain.org>" --prod
   ```
4. Sign up with your own address on the live site and check the email arrives, renders, and the confirm and unsubscribe links work.
5. Email everyone who signed up while sending was off (only pending addresses never emailed):
   ```sh
   npx convex run email:sendPendingWelcomes --prod
   ```

The email copy is in `convex/lib.ts` (`buildWelcomeEmail`); the group name, goal line and subject are in `convex/constants.ts`. To rename to "Read Indus", edit `GROUP_NAME` there and run `npx convex deploy`.

## Owner tasks

```sh
npx convex run subscribers:counts --prod            # counts by status
npx convex run subscribers:exportConfirmed --prod   # confirmed emails, confirm dates, source page
npx convex run subscribers:exportConfirmed --prod > confirmed.json   # save to a file (do not commit it)
```

Delete a subscriber on request (removes the row entirely):

```sh
npx convex run subscribers:deleteByEmail '{"email":"person@example.com"}' --prod
```

If they only want to stop emails, unsubscribing is enough; deletion is for "erase my data".

## Develop and deploy

```sh
npm install
npm test                 # unit + in-memory HTTP tests (convex-test, vitest)
npx convex dev --once    # push to dev once (no watcher)
npx convex deploy        # push to production
```

## Removing everything

1. Remove the form from the site.
2. Export anything you want to keep (`exportConfirmed`).
3. Delete the project in the Convex dashboard: open the `open-indus-newsletter` project, Project Settings, Delete Project. This deletes both deployments and all data.
4. Delete this folder.
5. If you set up Resend: revoke the API key and remove the DNS records.

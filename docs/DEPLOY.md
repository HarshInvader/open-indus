# Deploying the site

The site is static and is served from Cloudflare Pages at https://openindus.pages.dev (project `openindus`). It is an unlisted preview: every page carries `noindex, nofollow` while `PREVIEW = True` in `site/build.py`.

1. Build from the repo root:

   ```
   nice .venv/bin/python -I site/build.py
   ```

   This writes the pages, checks every internal link (and stops on a broken one), and writes the upload set to `site/dist/`.
2. Deploy `site/dist/`:

   ```
   cd site && npx wrangler pages deploy dist --project-name openindus --branch main --commit-dirty=true
   ```

   You need a Wrangler login with access to the project.
3. Check the live pages, for example `/library` and `/news`. Cloudflare redirects `x.html` to `x`.

The library page reads `docs/library/library.json`, and the news pages read the build's news items. Rebuild and redeploy after either changes.

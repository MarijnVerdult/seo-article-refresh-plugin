# AIHR SEO Plugins

Public marketplace repo for Codex and Cloud Cowork plugins used in AIHR SEO workflows.

## Install in Codex

1. Open the Codex Desktop application.
2. Open **Customize → Plugins**.
3. Choose **Add marketplace**.
4. Enter `MarijnVerdult/seo-article-refresh-plugin` and add the marketplace.
5. Install **SEO Article Audit** from the plugin list.
6. Complete the Google sign-in prompt for **AIHR GSC API** when Codex asks for it.

During install, Codex should open a browser for Google sign-in (PKCE) so the bundled **AIHR GSC API** MCP connector can call Search Console. Only verified `@aihr.com` Workspace accounts are accepted. **Outline** uses OAuth at connect time (sign in to the AIHR Outline workspace). **Ahrefs** uses its own connector auth when you run the full audit workflow.

## Install in Cloud Cowork

### From GitHub marketplace

1. Open **Customize → Plugins** in Cowork.
2. **Add marketplace** and enter `MarijnVerdult/seo-article-refresh-plugin` (or the full GitHub URL).
3. Install **SEO Article Audit**.

### From a local file (no marketplace)

A packaged Cowork bundle is built at `../seo-article-audit.plugin` (v2.7.6). Rebuild anytime:

```sh
./scripts/package-cowork-plugin.sh
```

Install in Cowork:

1. Open **Customize → Plugins**.
2. Use **Upload plugin** and select `seo-article-audit.zip` (or rename `.plugin` → `.zip` if upload rejects `.plugin`).
3. Complete Google sign-in when prompted for **AIHR GSC API**.

If install completes without a sign-in prompt, remove and reinstall the plugin after the marketplace cache refreshes, or contact your admin if the org pins an older marketplace snapshot.

## Included Plugin

### `seo-article-audit`

This plugin bundles four skills:

- `seo-article-audit`: diagnoses why an AIHR article declined in organic traffic, checks prior Outline analysis, compares GSC query performance, evaluates Ahrefs keyword facts and fact-only SERP observations for primary and secondary keywords, then returns a human-in-the-loop salvage strategy before optimization work begins.
- `serp-analysis`: gathers fact-only observations from a US-localized Google SERP for a primary or secondary keyword, including observed search intent, AI Overview, SERP features, ads, image/video modules, exact related searches, exact People Also Ask questions, organic result links, and screenshot evidence.
- `article-diff-md`: formats pre-marked article edits into one GitHub-style red/green Markdown diff block.
- `outline-article-refresh-memory`: proactively creates and maintains monthly Outline records during SEO article refresh work, including prior-record checks, supporting file attachments, final diff blocks, and collection overview/table-of-contents updates.

## Contents

- `.agents/plugins/marketplace.json` — Codex marketplace manifest (`authentication: ON_INSTALL`).
- `.claude-plugin/marketplace.json` — Cloud Cowork / Claude marketplace manifest (`authentication: ON_INSTALL`).
- `plugins/seo-article-audit/.codex-plugin/plugin.json` — Codex plugin manifest.
- `plugins/seo-article-audit/.claude-plugin/plugin.json` — Cowork plugin manifest.
- `plugins/seo-article-audit/.mcp.json` — remote AIHR GSC API, Ahrefs, and Outline MCP endpoints.
- `plugins/seo-article-audit/skills/` — plugin skill instructions and helper scripts.

## Requirements

- Network access to `https://gsc-mcp.aihr.com`, `https://api.ahrefs.com`, and `https://aihr.getoutline.com`.
- Google login with an `@aihr.com` Workspace account (requested at plugin install).
- Outline login when connecting the bundled Outline MCP server ([Outline MCP docs](https://docs.getoutline.com/s/guide/doc/mcp-6j9jtENNKL)); workspace admins must keep MCP enabled under **Settings → AI**.
- Ahrefs MCP access when running the full audit workflow (separate connector auth as required by Ahrefs).

OAuth tokens are stored by Codex or Cowork after install — not in a local plugin cache file.

## License

Proprietary. Public visibility of this repository does not grant an open-source license.

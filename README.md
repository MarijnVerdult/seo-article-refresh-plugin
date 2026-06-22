# AIHR SEO Plugins

Public marketplace repo for Codex and Cloud Cowork plugins used in AIHR SEO workflows.

## Install in Codex

```sh
codex plugin marketplace add MarijnVerdult/seo-article-refresh-plugin --ref main --sparse .agents/plugins --sparse plugins
codex plugin add seo-article-audit@aihr-seo-plugins
```

During install, Codex should open a browser for Google sign-in (PKCE) so the bundled **AIHR GSC API** MCP connector can call Search Console. Only verified `@aihr.com` Workspace accounts are accepted.

## Install in Cloud Cowork

1. Open **Customize → Plugins** in Cowork.
2. **Add marketplace** and enter `MarijnVerdult/seo-article-refresh-plugin` (or the full GitHub URL).
3. Install **SEO Article Audit**.

If the plugin includes a connector that needs authentication, Cowork should prompt you to sign in during or right after install — a browser tab or in-app sign-in flow for Google (`@aihr.com`). The GSC MCP server is `https://aihr-gsc-api.vercel.app/mcp`; tool name `seo_article_audit_gsc`.

If install completes without a sign-in prompt, remove and reinstall the plugin after the marketplace cache refreshes, or contact your admin if the org pins an older marketplace snapshot.

## Included Plugin

### `seo-article-audit`

This plugin bundles two skills:

- `seo-article-audit`: pulls Google Search Console query data for an AIHR article, combines it with Ahrefs keyword and content-gap data, and produces a static Excel workbook plus Markdown analysis.
- `article-diff-md`: formats pre-marked article edits into one GitHub-style red/green Markdown diff block.

## Contents

- `.agents/plugins/marketplace.json` — Codex marketplace manifest (`authentication: ON_INSTALL`).
- `.claude-plugin/marketplace.json` — Cloud Cowork / Claude marketplace manifest (`authentication: ON_INSTALL`).
- `plugins/seo-article-audit/.codex-plugin/plugin.json` — Codex plugin manifest.
- `plugins/seo-article-audit/.claude-plugin/plugin.json` — Cowork plugin manifest.
- `plugins/seo-article-audit/.mcp.json` — remote AIHR GSC API and Ahrefs MCP endpoints.
- `plugins/seo-article-audit/skills/` — plugin skill instructions and helper scripts.

## Requirements

- Network access to `https://aihr-gsc-api.vercel.app`.
- Google login with an `@aihr.com` Workspace account (requested at plugin install).
- Ahrefs MCP access when running the full audit workflow (separate connector auth as required by Ahrefs).

OAuth tokens are stored by Codex or Cowork after install — not in a local plugin cache file.

## License

Proprietary. Public visibility of this repository does not grant an open-source license.

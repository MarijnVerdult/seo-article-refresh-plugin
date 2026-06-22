# AIHR SEO Plugins

Public marketplace repo for Codex and Claude plugins used in AIHR SEO workflows.

## Install in Codex

```sh
codex plugin marketplace add MarijnVerdult/seo-article-refresh-plugin --ref main --sparse .agents/plugins --sparse plugins
codex plugin add seo-article-audit@aihr-seo-plugins
```

## Install in Claude Code

```sh
claude plugin marketplace add MarijnVerdult/seo-article-refresh-plugin --sparse .claude-plugin plugins
claude plugin install seo-article-audit@aihr-seo-plugins
```

## Included Plugin

### `seo-article-audit`

This plugin bundles two skills:

- `seo-article-audit`: pulls Google Search Console query data for an AIHR article, combines it with Ahrefs keyword and content-gap data, and produces a static Excel workbook plus Markdown analysis.
- `article-diff-md`: formats pre-marked article edits into one GitHub-style red/green Markdown diff block.

## Contents

- `.agents/plugins/marketplace.json` - Codex marketplace manifest.
- `.claude-plugin/marketplace.json` - Claude Code marketplace manifest.
- `plugins/seo-article-audit/.codex-plugin/plugin.json` - Codex plugin manifest.
- `plugins/seo-article-audit/.claude-plugin/plugin.json` - Claude plugin manifest.
- `plugins/seo-article-audit/.mcp.json` - MCP server configuration for the remote AIHR GSC API and Ahrefs MCP endpoint.
- `plugins/seo-article-audit/skills/` - plugin skill instructions and helper scripts.

## Requirements

- Network access to `https://aihr-gsc-api.vercel.app`.
- Google login with an `@aihr.com` Workspace account.
- Access to the Ahrefs MCP server configured in `.mcp.json` when running the full audit workflow.

On first GSC use, your IDE completes OAuth against Google (PKCE). Only verified `@aihr.com` Workspace accounts are accepted. Tokens are stored by Claude Code / Cursor / Codex — not in a local plugin cache.

### Connect the GSC MCP server

After installing the plugin, open MCP settings (`/mcp` in Claude Code) and connect **AIHR GSC API** when prompted. The server exposes tool `seo_article_audit_gsc`.

### Cursor OAuth note

Cursor uses redirect URI `cursor://anysphere.cursor-mcp/oauth/callback`. If Connect fails with the existing Desktop OAuth client, create a **Web application** OAuth client in Google Cloud Console with that redirect URI and add its public client ID to `.mcp.json` under `oauth.clientId` (see `aihr-gsc-api/OAUTH.md` in the parent workspace).

## License

Proprietary. Public visibility of this repository does not grant an open-source license.

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
- `plugins/seo-article-audit/.mcp.json` - MCP server configuration for the local GSC bridge and Ahrefs MCP endpoint.
- `plugins/seo-article-audit/bin/seo-article-audit-server` - executable wrapper for the local stdio MCP server.
- `plugins/seo-article-audit/servers/seo_article_audit_server.py` - stdio MCP server that fetches GSC reports from AIHR's GSC API.
- `plugins/seo-article-audit/skills/` - plugin skill instructions and helper scripts.

## Requirements

- Python 3.
- Network access to `https://aihr-gsc-api.vercel.app`.
- Access to the Ahrefs MCP server configured in `.mcp.json` when running the full audit workflow.

## Local Check

From this folder, the local MCP server should respond to initialization and tool listing:

```sh
printf '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}\n{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}\n' | ./plugins/seo-article-audit/bin/seo-article-audit-server
```

## License

Proprietary. Public visibility of this repository does not grant an open-source license.

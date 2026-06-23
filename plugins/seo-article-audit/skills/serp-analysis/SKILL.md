---
name: serp-analysis
description: >-
  Gather factual observations from a Google SERP for one SEO keyword in the US using live browser
  capture only. Use when the SEO Article Audit workflow needs a screenshot and observed SERP inventory
  for AI Overview, People Also Ask, people-also-search-for, ads, image modules, Reddit/YouTube/forum
  presence, blue links, observed search intent, or other SERP features for a primary or secondary keyword.
  Never use Ahrefs in this skill. This skill reports only what is visible
  on the live Google SERP; the parent SEO audit agent performs ranking-realism assessment and article recommendations.
---

# SERP Analysis

## Purpose

Gather factual observations from the live US Google SERP for a single keyword and return a structured inventory that can inform an SEO article audit or refresh.

This skill is the **only** approved source for SERP inventory in the SEO Article Audit plugin. The parent auditor must not use Ahrefs SERP tools as a substitute.

## Tool Routing (Mandatory)

| Allowed | Forbidden |
| --- | --- |
| **Browser** navigation to `https://www.google.com/search` with the US URL template in `references/serp-screenshot-procedure.md` | **Any Ahrefs MCP call** |
| **Browser** snapshot / DOM inspection for visible modules, links, PAA, ads, AI Overview | Ahrefs **`serp-overview`**, **`rank-tracker-serp-overview`**, SERP rows, rank-index exports |
| **Browser** full-page screenshot per the reference procedure | Ahrefs **`site-explorer-*`**, **`gsc-*`**, **`keywords-explorer-*`**, or any other Ahrefs endpoint |
| | Using Ahrefs to infer organic result order, SERP features, or AI Overview content |

If browser access fails, report the failure and stop SERP collection. Do **not** fall back to Ahrefs.

### Browser requirement

Use live browser automation:

- **Cursor:** `cursor-ide-browser` MCP — `browser_navigate`, `browser_snapshot`, `browser_take_screenshot`, and related interaction tools.
- **Codex / Cowork:** Codex Chrome extension workflow described in `references/serp-screenshot-procedure.md`.

Read `references/serp-screenshot-procedure.md` before the first screenshot. Every SERP fact in the output must trace to what the browser showed on the live Google page.

This skill is suitable for:

- The primary keyword chosen by the SEO Article Audit workflow.
- Secondary keywords that need separate intent or SERP-feature checks.
- Standalone requests to inspect a keyword SERP.

For full SEO article audits, the parent agent should delegate this skill's workflow to a sub-agent when sub-agents are available. The sub-agent's job is SERP evidence collection only. The sub-agent should assume it has not read AIHR's article and must not make article recommendations, judge AIHR's ranking realism, or infer what AIHR should change. It may classify observed search intent from the visible SERP composition because that is a factual SERP observation.

## Required Inputs

- `keyword` — the exact keyword to analyze.
- `market` — default `US`.
- Optional keyword role: primary or secondary. Use this for labeling only.

Do not use Ahrefs in this skill. Do not call the Ahrefs MCP. Do not accept Ahrefs SERP rows, Ahrefs SERP Overview output, rank-index exports, or any other Ahrefs data as input or evidence.

## Gotcha — full UULE on every SERP

Every SERP capture must use the complete US-localized Google URL from `references/serp-screenshot-procedure.md`, including the full fixed `uule=...` parameter. This is mandatory for **every** keyword run — primary **and** secondary. Keyword role is labeling only; it does not relax URL requirements.

Do not omit UULE, truncate it, substitute a different geolocation value, or fall back to a plain `?q=...` search URL. Each primary and secondary keyword needs its own fresh browser navigation with the full parameter set (`hl=en`, `gl=US`, `pws=0`, and the complete UULE string). A secondary-keyword SERP is not a shortcut run.

If the captured URL is missing the full UULE, discard the capture and redo it before reporting SERP facts.

## Core Output Questions

Answer these fact-only questions:

1. What SERP features are visible?
2. Which pages, domains, and page types are visible in organic results?
3. What does the AI Overview show, if present?
4. Which questions, related searches, ads, images, videos, forums, or other modules are visible?
5. What search intent is indicated by the visible SERP composition?

Do not answer whether AIHR can rank, what AIHR should write, what subheaders to add, or what FAQs to include. Those are main-auditor responsibilities.

## Workflow

1. Build the US-localized Google SERP URL for the keyword with the full fixed UULE — see **Gotcha — full UULE on every SERP** and `references/serp-screenshot-procedure.md`.
2. Open the URL in a **browser** tab. Do not open Ahrefs.
3. Capture a full-page screenshot using the reference procedure.
4. Inspect the live SERP and screenshot for:
	1. AI Overview: whether present, visible text summary, cited/source types, and whether visible sources include YouTube, Reddit, forums, definitions, tools, lists, or article-style pages.
	2. Search intent: observed dominant and secondary intent labels, grounded in visible SERP composition and page types.
	3. People Also Ask: every visible question, in visible order.
	4. People also search for / related searches: every visible related query, in visible order.
	5. Organic blue links: ranking page titles, full visible URLs or hrefs, domains, snippets, and observable page types.
	6. Image pack and image tab: whether present and what image topics/types are visible.
	7. Things to know or other exploratory modules when present.
	8. Ads: presence, position, advertiser/domain, visible copy, and landing page when visible.
	9. Video, Reddit, forum, tool, job board, dictionary, government, university, or vendor modules.
5. Return a structured factual report with evidence and caveats.

Read `references/serp-screenshot-procedure.md` before taking screenshots.

**Hard stop:** do not use Ahrefs in this skill. Never call Ahrefs MCP tools. Never paste Ahrefs data into any output section. SERP facts must come only from the live browser capture.

In **SERP Evidence Used**, state explicitly:

```text
Live Google SERP via browser (screenshot-backed)
```

## Output Contract

Return Markdown with these sections:

```text
Keyword
SERP Evidence Used
Observed Search Intent
SERP Feature Inventory
AI Overview
Organic Results
People Also Ask
Related Searches
Ads
Images And Video
Forums, Reddit, And UGC
Other SERP Modules
Caveats
Screenshot
```

**SERP Evidence Used** must confirm browser capture only. If Ahrefs or any third-party SERP source was used, the output is invalid — redo the capture with the browser workflow.

Keep all content scoped to observed evidence. Do not include "Ranking Realism", "Implications For AIHR", "Recommendations", "Opportunities", or similar article-strategy sections.

Do not state SERP feature evolution or click impact as facts unless backed by provided source data.

## Required Detail Level

Return concrete SERP items, not summaries only:

- Organic results: include rank/order, title, URL or href, domain, visible snippet, and observed page type for every visible result captured in the screenshot.
- Competitor/result links: include the full URL or href whenever visible or available from the DOM.
- People Also Ask: include the exact visible question text for each question.
- People also search for / related searches: include the exact visible query text for each query.
- AI Overview citations/sources: include visible source names and links/hrefs when visible or available from the DOM.
- Ads: include visible advertiser/domain and landing URL/href when visible or available from the DOM.
- Images/videos/modules: include visible titles, source domains, and links/hrefs when visible or available from the DOM.

## Fact-Only Boundaries

Do not:

- Use Ahrefs in any form — no MCP calls, no pasted exports, no keyword facts passed through this skill.
- Read or evaluate AIHR's article unless explicitly asked by the parent agent for a separate task.
- Suggest subheaders, FAQs, images, secondary keywords, rewrites, or content changes.
- Judge whether AIHR can rank top 3 or top 5.
- Convert observed data into strategy.

Allowed neutral labels include:

```text
Observed search intent: informational, commercial, transactional, navigational, local, mixed.

Observed page types: guide, definition, tool, product page, vendor page, course page, job board, dictionary, government page, university page, video, forum thread, Reddit thread, image result.

Observed module types: AI Overview, PAA, related searches, ads, image pack, video carousel, knowledge panel, Things to know.
```

## Sub-Agent Handoff Guidance

When a parent SEO audit agent delegates this work, pass:

- Exact keyword.
- Whether it is primary or secondary.
- Required screenshot output location or filename convention.

Do not pass Ahrefs data to this skill. Keyword difficulty and volume are gathered separately by the parent auditor via Ahrefs — not inside `serp-analysis`.

Do not pass the full article unless there is a separate, explicit reason. Ask the sub-agent to return only the structured factual output contract plus the screenshot path.

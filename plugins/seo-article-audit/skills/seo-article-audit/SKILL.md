---
name: seo-article-audit
description: >-
  Diagnose why a specific AIHR article declined in organic traffic and decide whether
  there is a viable SEO salvage strategy. Use when someone asks why an AIHR article has
  declined, whether it can be salvaged, what happened to traffic for a URL, or what primary
  or secondary keyword strategy to pursue. Tool routing is strict: GSC via AIHR GSC API MCP
  (fetch_article_keyword_performance), Ahrefs for keyword difficulty and volume only
  (keywords-explorer-overview), live SERP via the bundled serp-analysis browser skill — never Ahrefs SERP.
  The workflow reads the article, checks prior Outline analysis, derives the primary keyword from the slug,
  pulls 6-month Google Search Console query comparisons for the exact page, identifies potential secondary
  keywords, and reports a human-in-the-loop strategy recommendation without suggesting article optimizations yet.
---

# SEO Article Audit

## Purpose

Answer this kind of prompt:

```text
The HR Generalist article has declined in traffic, why?
https://www.aihr.com/blog/hr-generalist/
And is there an opportunity to salvage it?
```

The output is a diagnostic strategy report, not an optimization plan. Stop after explaining the
decline, the keyword landscape, and the recommended strategy direction. Do not suggest rewrites,
new sections, FAQs, titles, briefs, or on-page optimizations until the human has reviewed and
discussed the strategy.

## Workflow Summary

1. Read the article and create a full-article artifact.
2. Inspect Outline for previous analysis of this article.
3. Derive the primary keyword from the slug.
4. Pull Ahrefs keyword difficulty and search volume for the primary keyword.
5. Delegate fact-only SERP analysis for the primary keyword.
6. Pull exact-page GSC query data for a 6-month comparison.
7. Identify potential secondary keyword candidates from GSC.
8. Pull Ahrefs difficulty/volume and delegate live-Google SERP analysis for selected secondary keyword(s).
9. Decide the strategy direction and report back for human review.
10. Update Outline with the strategy report — do not skip this after delivering the report to the user.

## Tool Routing (Mandatory)

This audit uses **three separate tools**. Each has one job. Do not substitute one for another.

| Data need | Required source | Required method |
| --- | --- | --- |
| Page traffic, query clicks, impressions, position, CTR, 6-month decline | **Google Search Console** | MCP server **`AIHR-GSC-API`** → tool **`fetch_article_keyword_performance`** with the normalized AIHR URL |
| Keyword difficulty and search volume only | **Ahrefs** | MCP server **`ahrefs`** → tool **`keywords-explorer-overview`** for the keyword in **`US`**; read only **keyword difficulty** and **search volume** |
| SERP features, organic results, AI Overview, PAA, ads, intent, screenshot | **Live Google SERP** | Bundled skill **`serp-analysis`** via **browser** (navigate to `google.com/search`, capture screenshot, inspect DOM) |

### Google Search Console rules

- **Always** use the bundled **`AIHR-GSC-API`** MCP at `https://gsc-mcp.aihr.com/mcp`.
- **Always** call **`fetch_article_keyword_performance`**. It returns US traffic with current vs previous 6-month page and query metrics.
- **Never** use Ahrefs GSC tools (`gsc-pages`, `gsc-keywords`, `gsc-page-history`, or any other `gsc-*` Ahrefs endpoint) for this audit. Ahrefs GSC is not the packaged GSC source.
- **Never** infer traffic decline from Ahrefs traffic estimates, `site-explorer-*` metrics, or rank-tracker data when GSC is available.

### Ahrefs rules

- **Allowed:** one call pattern only — **`keywords-explorer-overview`** to get **keyword difficulty** and **search volume** for a specific keyword in the US.
- **Forbidden for this audit:** any Ahrefs SERP or rank-index source, including **`serp-overview`**, **`rank-tracker-serp-overview`**, and any export labeled SERP Overview, SERP rows, or rank index.
- **Also forbidden:** `site-explorer-organic-keywords`, `site-explorer-organic-competitors`, `keywords-explorer-related-terms`, `keywords-explorer-matching-terms`, backlink tools, and any other Ahrefs endpoint. This audit does not use Ahrefs for competitors, content gaps, SERP composition, or page-level organic data.
- If Ahrefs keyword metrics are unavailable, continue the audit and state the gap. Do **not** backfill with Ahrefs SERP or site-explorer data.

### SERP rules

- **Always** gather SERP evidence through the bundled **`serp-analysis`** skill using a **live browser**.
- **Never** call Ahrefs **`serp-overview`** or **`rank-tracker-serp-overview`** for SERP inventory, intent, modules, or ranking realism.
- **Never** paste Ahrefs SERP rows into Primary SERP Facts or Secondary SERP Facts. Those sections may only contain output from **`serp-analysis`** plus its screenshot path.
- When sub-agents are available, delegate **`serp-analysis`** as a fact-only sub-task. When they are not, run **`serp-analysis`** directly yourself — still via browser, not Ahrefs.

### Decision checks before each pull

Before calling a tool, confirm:

```text
Need query-level clicks/impressions/position for this exact AIHR URL?
  → AIHR-GSC-API / fetch_article_keyword_performance

Need difficulty or volume for one keyword?
  → ahrefs / keywords-explorer-overview (US only; difficulty + volume fields only)

Need what Google actually shows for a keyword (features, links, AI Overview, PAA, ads)?
  → serp-analysis skill + browser screenshot workflow
  → STOP if you are about to open serp-overview or any Ahrefs SERP tool
```

## Guardrails

- The main goal is to recover clicks. Rankings are an input because rankings can lead to clicks,
  but ranking is not the primary goal.
- Always evaluate ranking opportunity through the visible SERP layout. If AI Overview, sponsored
  results, image packs, People Also Ask, videos, or other modules push blue links down, a high
  organic rank may still produce weak clicks.
- Stop at strategy. Do not provide article optimizations yet.
- Separate data gathering from interpretation.
- Follow **Tool Routing (Mandatory)** for every data pull. Wrong-tool data is invalid for this audit.
- Treat `serp-analysis` outputs as the only SERP inventory evidence. The main auditor owns interpretation.
- For Google SERP capture, require the user's real browser profile. In Codex, use the Codex Chrome plugin / Codex Chrome Extension. In Claude Cowork, use Claude Cowork browser control or Claude in Chrome. Do not use standalone Playwright, bundled/headless Chromium, or the in-app browser unless the user explicitly approves that fallback after the user-browser path fails.
- If data is unavailable, continue with the remaining evidence and state the gap.
- Do not overfit to one metric. Use article content, Ahrefs keyword metrics, SERP facts, and GSC together.
- Be explicit about what is observed vs inferred.

## 1. Normalize The URL

- Must be an AIHR URL under `https://www.aihr.com/`.
- If the user gives a path such as `/blog/hr-generalist/`, prepend `https://www.aihr.com`.
- Ensure exactly one trailing slash.
- Slug is the last non-empty path segment, e.g. `hr-generalist`.

## 2. Read The Article And Create A Full-Article Artifact

Read the current article before interpreting performance.

Create a Markdown artifact named:

```text
seo-article-audit-<slug>-full-article.md
```

The artifact should contain only the full article content:

```text
Title/H1
Full article body
```

Do not put audit notes, metadata summaries, GSC data, Ahrefs data, SERP findings, or strategy
comments in this artifact. It is a clean copy of the article only, used as source context.

## 3. Inspect Outline For Prior Analysis

Use the bundled `outline-article-refresh-memory` skill before producing conclusions. Check whether
there is a previous monthly record for the article slug or a closely related record.

If prior analysis exists, summarize only the relevant facts:

```text
Prior record title/date
What was previously diagnosed
What strategy or work was previously recommended
Any attached files or notes that matter for this audit
```

If none exists, say no prior Outline analysis was found.

## 4. Determine The Primary Keyword

Start from the slug and convert it into a natural keyword:

```text
hr-generalist -> hr generalist
```

Use this as the primary keyword unless GSC or the article itself strongly indicates that the page is
clearly targeting a different head term. If changing the primary keyword candidate at this stage,
explain why and keep the slug-derived keyword as a checked alternative.

## 5. Pull Ahrefs Keyword Metrics For The Primary Keyword

Use the **`ahrefs`** MCP server. Call **`keywords-explorer-overview`** for the primary keyword with **`country: US`**.

Extract and report only:

```text
keyword difficulty
search volume
```

Do not request or use any other Ahrefs fields for strategy in this step (CPC, traffic potential, parent topic, SERP features, ranking URLs, etc.).

Interpretation thresholds:

```text
Keyword difficulty 25+ = hard.
Search volume 200+ = attractive.
For B2B HR topics, search volume 30+ can still be meaningful.
```

These are heuristics, not absolute rules. A lower-volume B2B keyword can still be viable if intent is
strong and SERP fit is realistic.

**Hard stop:** do not call **`serp-overview`**, **`rank-tracker-serp-overview`**, or any other Ahrefs SERP or site-explorer tool in this audit. SERP composition belongs exclusively to **`serp-analysis`**.

## 6. Delegate Primary Keyword SERP Analysis

Use the bundled **`serp-analysis`** skill as the contract for a fact-only sub-agent task when sub-agents
are available. The sub-agent must use the environment's **user-browser** tools to open the live Google SERP — not Ahrefs and not a bundled/headless browser.

Pass only:

```text
keyword
keyword role: primary
market: US
required screenshot filename/path
browser requirement: user browser only; Codex → Codex Chrome plugin / Codex Chrome Extension; Claude Cowork → Claude Cowork browser control or Claude in Chrome; no standalone Playwright, bundled/headless Chromium, or in-app browser without explicit user-approved fallback
```

Do not pass Ahrefs data into **`serp-analysis`**. Ahrefs keyword metrics stay in the parent audit; SERP collection is browser-only.

Do not ask the SERP sub-agent to read the AIHR article or recommend optimizations. It should return
observed search intent, exact People Also Ask questions, exact related searches / people-also-search-for
queries, organic result links, SERP modules, ads, AI Overview facts, caveats, and screenshot path.

If sub-agents are not available, run the **`serp-analysis`** workflow directly and keep the same fact-only
boundary and user-browser requirement.

The SERP evidence must be gathered from live Google using **`serp-analysis`** only. Do not use Ahrefs inside that skill or to fill Primary SERP Facts. If the correct user browser cannot be reached, stop SERP collection and ask the user to connect/enable the browser add-on/profile rather than continuing with another browser.

## 7. Pull GSC Exact-Page Query Data

Call the **`AIHR-GSC-API`** MCP server. Use tool **`fetch_article_keyword_performance`** with the exact normalized page URL.

This is the only GSC source for this audit. Do not call Ahrefs `gsc-*` tools or legacy REST endpoints.

The tool returns US data as current vs previous 6-month windows with page totals and query rows sorted by largest click loss first.

From the response, identify:

```text
Total clicks: current vs previous
Total impressions: current vs previous
Average CTR: current vs previous
Average position: current vs previous
Queries that currently bring clicks
Queries that previously brought clicks
Queries with the largest click losses
Queries with large impression volume but weak CTR
Queries with average positions near striking distance, especially positions 4-20
Queries where rankings dropped materially
Queries where impressions changed materially
```

Keep raw query facts separate from interpretation.

## 8. Determine Potential Secondary Keywords

Select secondary keyword candidates from GSC query data. Prioritize candidates that have at least one
of these signals:

```text
Meaningful current or previous clicks
High or growing impressions
Average position in or near striking distance
Clear relevance to the article topic
Distinct intent from the primary keyword
Potential to explain the decline or salvage opportunity
```

Do not select a secondary keyword just because it has high impressions. It must be relevant and have
some realistic path to useful traffic.

For selected secondary keyword candidates, repeat the keyword checks with the same tool boundaries:

```text
ahrefs / keywords-explorer-overview → keyword difficulty + search volume only
serp-analysis skill + browser → live SERP inventory + screenshot
```

For secondary keywords, the same routing applies: **`keywords-explorer-overview`** for metrics only; **`serp-analysis`** for every SERP fact. Never use **`serp-overview`** or any Ahrefs SERP export.

It is acceptable to analyze one strong secondary keyword first. Analyze more only when the GSC data
shows multiple plausible directions.

## 9. Determine Strategy Direction

Use all evidence to choose one of these strategy directions:

```text
Double down on the primary keyword.
Switch the primary keyword only if intent has changed and another keyword has a better opportunity.
Keep the primary keyword, but double down on secondary keywords.
Deprioritize or stop investing if the SERP and demand no longer support a realistic salvage path.
```

Strategy criteria:

- Primary keyword viability depends on observed search intent, Ahrefs difficulty/volume, SERP
  composition, AI Overview pressure, competing page types, and GSC evidence.
- Secondary keyword viability depends on GSC query evidence, Ahrefs difficulty/volume, SERP facts,
  and relevance to the article's current or plausible scope.
- A keyword is only strategically useful if it can plausibly recover clicks. Strong ranking potential
  is not enough when SERP features or ads make organic clicks unlikely.
- A strategy can be mixed, e.g. keep the primary keyword while using secondary keywords as the
  traffic recovery path.

Do not suggest concrete optimizations yet.

## Final Output

Return a Markdown strategy report with these sections:

```text
Article Reviewed
Prior Analysis Checked
Traffic Decline Summary
Primary Keyword Facts
Primary SERP Facts
GSC Query Findings
Secondary Keyword Candidates
Secondary SERP Facts
Strategy Recommendation
Why This Strategy
Open Questions For Human Review
Artifacts
```

The final report should answer:

```text
Why did the article decline?
Is the primary keyword still viable?
Is there a better secondary keyword opportunity?
Is there an opportunity to salvage the article?
Which path is most likely to recover clicks, not just rankings?
Which strategy should we discuss before optimization work begins?
```

End by asking the human to confirm or challenge the strategy before any optimization plan is created.

## Gotcha — update Outline after the strategy report

Delivering the strategy report to the user is not the end of the audit. **Immediately after** you report back, use the bundled **`outline-article-refresh-memory`** skill to create or update the current monthly Outline record for this article.

Do not wait for the user to ask. Do not assume step 3 (checking prior Outline analysis) satisfies documentation — that step is read-only at the start.

Capture at minimum:

```text
Traffic decline summary and key GSC query findings
Primary and secondary keyword facts (Ahrefs difficulty/volume)
Strategy recommendation and why
Open questions for human review
Links or references to audit artifacts (full-article file, SERP screenshots, etc.)
```

If you create a new monthly record, update the collection overview/table of contents per **`outline-article-refresh-memory`**. Return the Outline document link when done.

If an Outline create/update action is blocked, rejected, or requires user approval, stop immediately and ask: "Do I have your approval to save this SEO audit record to the AIHR-seo-article-refresh Outline collection?" Do not defer this to the final answer, do not silently skip the memory update, and do not treat the audit as complete until Outline is updated or the user explicitly declines/withholds approval.

## What Not To Do

- Do not produce a rewrite plan.
- Do not suggest headings, FAQs, title tags, meta descriptions, images, or content additions.
- Do not create final article diffs.
- Do not treat the SERP sub-agent as an article strategist.
- Do not skip reading the article.
- Do not skip GSC if the question is about traffic decline.
- Do not finish the audit after the strategy report without updating Outline via **`outline-article-refresh-memory`**.
- Do not reduce an Outline write approval/rejection to a final-answer caveat. Ask for approval immediately and retry the Outline write if the user approves.
- Do not use Ahrefs for SERP data (`serp-overview`, `rank-tracker-serp-overview`, SERP rows, rank-index exports).
- Do not use Ahrefs `gsc-*` tools or site-explorer endpoints when the bundled GSC MCP or keyword metrics call exists.
- Do not fill Primary SERP Facts or Secondary SERP Facts without a **`serp-analysis`** screenshot-backed browser capture.

---
name: seo-article-audit
description: >-
  Audit the search performance of any AIHR article URL. Pulls Google Search Console
  page- and query-level click/impression metrics across two consecutive 6-month windows
  (US only, sorted by click loss) AND Ahrefs organic keywords (including dropped keywords) for the same URL via
  the Ahrefs MCP server, plus a content-gap analysis of that page against 2–4 intent-selected
  organic competitors (also via Ahrefs). It then writes a static Excel workbook (GSC queries +
  Ahrefs keywords + Content gap sheets) plus a Markdown analysis. Use whenever someone asks to "audit this article",
  "audit the SEO for X", "get GSC + Ahrefs data for X", "show me the search performance of X",
  "what queries/keywords is X losing", "run a content gap analysis for X", or "how is X doing in search" — for a specific AIHR URL.
---

# SEO article audit

## What this does

For a single AIHR page URL this skill runs a small pipeline and produces **static artifacts**
(downloadable files written to the outputs folder and shared with `present_files`). A static
artifact is a downloadable file that does NOT render interactively. So:

- Do NOT call `show_widget` (that is an inline chat widget).
- Do NOT call `create_artifact` / `update_artifact` (those are live, side-panel artifacts).
- Do NOT write an interactive `.html`/`.jsx` file (an HTML file with JS renders live — that is a
  live artifact, not a static one).

**Output path — write once, present once.** The outputs folder is reachable by two paths that
point at the SAME physical directory: the shell/VM mount `/sessions/<session>/mnt/outputs/` and
the host path ending in `/outputs` used by the file tools and `present_files`. Build the files
with bash at the `/sessions/.../mnt/outputs/` path, then call `present_files` with the host
`/outputs` path. Do not infer the path from an intermediate tool-result location — those can
carry a stale session suffix. If a `Write` or `present_files` call is rejected as "outside
connected folders," it is a path-suffix mismatch, not a permissions problem: re-list the real
outputs directory and use that exact path.

Per run the skill emits, in order:

1. **One Excel workbook** `seo-article-audit-<slug>.xlsx` with three sheet tabs:
   - Sheet **"GSC queries"** — page-level summary + query-level breakdown (step 3).
   - Sheet **"Ahrefs keywords"** — the second tab — Ahrefs organic keywords, including dropped ones (step 4).
   - Sheet **"Content gap"** — the third tab — the intent-selected competitor pages and the keywords
     they rank for that this page does not (step 5).
2. **One Markdown analysis** `seo-article-audit-<slug>-analysis.md` — the written voiceover / editorial
   synthesis over all three sheets (step 7).

The Excel workbook is the intermediate data deliverable; the `.md` is the final analysis.

## Steps

### 1. Normalise the URL

- Must start with `https://www.aihr.com/`
- Strip trailing whitespace; ensure exactly one trailing slash
- If given a partial path like `/blog/raci-template/`, prepend `https://www.aihr.com`
- `<slug>` = the last non-empty path segment (e.g. `raci-template`), used in filenames.

### 2. Call the GSC MCP tool

```
mcp__plugin_seo-article-audit_seo-article-audit__seo_article_audit_gsc(url="<normalised_url>")
```

If the result starts with "Error:", surface it to the user and stop.

**Expect a large response.** For any real article this report is tens of thousands of
characters (a high-traffic page can have 700+ query rows) and will be auto-saved to a
tool-result file rather than returned inline. Do not try to read the whole thing into context.
Read only the header (periods + Page table) to capture dates, then parse the Queries table with
a script (grep/Python over the saved file). The same applies to the Ahrefs pull in Step 4.

### 3. Parse the GSC markdown response

The tool returns a markdown report with two tables. When the response was persisted to a file
(the usual case — see Step 2), parse that file with a script rather than reading it inline:

**Page table** (`## Page — same period comparison`): one row with current/previous clicks,
impressions, absolute deltas, and percentage deltas.

**Queries table** (`## Queries — same period comparison`): one row per query sorted by click
loss, with: rank, query, current clicks, previous clicks, Δ clicks (abs), Δ clicks (%),
current impr., previous impr., Δ impr. (abs), Δ impr. (%), avg pos now, avg pos prev, Δ avg pos.

Period labels appear as:
```
**Current period:** 2024-07-03 — 2025-01-01
**Previous period:** 2024-01-01 — 2024-07-02
```

Capture the current-period end date and previous-period end date — they are passed to Ahrefs.

### 4. Pull Ahrefs organic keywords via the Ahrefs MCP server

Collect keywords for the SAME normalised URL exactly the way the SEO article-refresh code does
it (`marketing/seo-article-refresh/skills/seo-article-enrichment/scripts/ahrefs.py`). That code
calls the Ahrefs `site-explorer/organic-keywords` endpoint; the equivalent Ahrefs MCP tool is
**`site-explorer-organic-keywords`** (Ahrefs MCP server, configured in this plugin's `.mcp.json`).

Follow the Ahrefs MCP server rules: call the connector's **`doc`** tool once per tool kind before
first use if it asks you to. If a response asks you to `render-data-table` / `render-scorecard`,
read the rows from that payload — but you still write the parsed rows into the Excel sheet; do not
leave any live render or runtime call in a deliverable.

Make the organic pull with the same parameters as `fetch_ahrefs_organic_keywords_for_url`:

- `target` = normalised URL
- `mode` = `exact`
- `country` = `us`
- `date` = GSC current-period end date; `date_compared` = previous-period end date
- `order_by` = `volume:desc,keyword:asc`
- `select` = `keyword,keyword_prev,language,keyword_country,volume,best_position,best_position_diff,best_position_prev`
- `limit` up to 2000, paginating in batches of 25 with a keyset cursor on `volume desc, keyword asc`
  when the connector returns partial pages.

This single organic pull already includes lost keywords — rows where `best_position` is null but
`best_position_prev` is set are keywords the URL has dropped out of. No separate lost-keyword
call is needed. Use `keyword` as the label, falling back to `keyword_prev` when `keyword` is null
(the usual case for a dropped keyword), same fallback as the SEO code.

**Normalise the pull to disk.** The organic pull may come back inline OR be auto-persisted to a
tool-result file, depending on size. Either way, write the rows to a JSON file before building
the workbook (redirect/save the inline result rather than transcribing rows by hand) so the
build step has one code path and no transcription errors.

If Ahrefs is unavailable (connector not enabled, auth/permission error, or no rows): continue with
GSC only, still produce the workbook, and put the reason in the "Ahrefs keywords" sheet header and
in the analysis `.md`. Do not fail the whole run.

### 5. Content-gap analysis vs intent-selected competitors (Ahrefs)

This reproduces the [Site Explorer Content Gap](https://ahrefs.com/content-gap) workflow at the
**page** (URL) level by chaining two Ahrefs MCP tools on the SAME Ahrefs MCP server used in step 4.
Call the connector's **`doc`** tool once per tool kind before first use if it asks you to. Use
`mode=exact` so overlaps are URLs, not whole sites, and reuse the GSC current-period end date as
`date` so the snapshot lines up with step 4.

**5a. Pull a WIDE candidate list (10–20 competitors).** Call **`site-explorer-organic-competitors`** with:

- `target` = normalised URL
- `mode` = `exact`
- `country` = `us`
- `date` = GSC current-period end date
- `order_by` = `keywords_common:desc`
- `select` = `competitor_url,keywords_common,keywords_competitor,share,domain_rating,traffic`
- `limit` = at least 20 (so there is a real pool to judge from — do NOT just take the top 3)

**5b. Select 2–4 competitors BY INTENT, not by a metric sort.** This is the core of the step.
`keywords_common` and `share` are both poor selectors on their own: a high `keywords_common` can come
from a large authority page that overlaps by accident (e.g. a certification or directory page sharing
a few generic HR terms), and a high `share` can come from a page that wins a single shared keyword over
a tiny overlap. **Do not pick the three highest rows by either column.** Instead, use judgment to choose
the 2–4 competitor pages whose **search intent matches this article's intent** — i.e. pages that are
genuinely trying to rank for the same thing this page is about.

To judge intent, look at signals such as: what the competitor page actually is (read its URL/path and,
if useful, its title — a salary guide vs a certification page vs a job board vs a university/government
careers page are different intents); whether the keywords it shares with this page are this page's
**money terms** (the head and mid-tail queries the article targets) rather than incidental overlap; and
whether the page is a credible same-type rival a human would compare this article against. Exclude pages
whose primary purpose differs from this article's even when their overlap or share looks high, and note
in one line (for the analysis `.md`) why each excluded-but-high-overlap page was dropped.

Aim for 2–4 selected competitors. It is acceptable — and better — to return only 2 strong same-intent
competitors than to pad the list to 3–4 with intent-mismatched pages. If fewer than 2 same-intent
competitors appear in the candidate pool, say so in the analysis and proceed with what is genuinely
comparable (or none). Record each selected competitor's `competitor_url`, `keywords_common`,
`keywords_competitor`, `share`, `domain_rating`, and `traffic`.

**5c. Pull each selected competitor's ranking keywords.** For **each** selected competitor URL, call
**`site-explorer-organic-keywords`** with:

- `target` = competitor URL
- `mode` = `exact`
- `country` = `us`
- `date` = same GSC current-period end date
- `where` = filter to genuinely-ranking terms, e.g. positions 1–10 (`best_position is one of lte 10`);
  use the schema form the `doc` tool returns
- `order_by` = `volume:desc`
- `select` = `keyword,volume,best_position` (minimal, to control API unit cost)
- small `limit` (e.g. 100), paginate only if needed

**5d. Compute the gap.** Build the set of keywords this page already ranks for from the step-4 organic
pull (`keyword`, falling back to `keyword_prev`). The **gap keywords** are the keywords appearing in any
selected competitor's pull that are absent from this page's keyword set. For each gap keyword, record its
`volume` and which competitor(s) rank it at position ≤10. Sort by `volume` desc and cap to a sensible
number of rows (e.g. top 100).

**Normalise to disk before merging**, same discipline as step 4: each competitor pull may come back inline
or be auto-persisted to a tool-result file — write each result set to a JSON file first, then compute the
gap from files (one code path, no hand transcription).

**Data only — no editorial in the sheet.** The competitor table and gap-keyword table are facts; the
intent rationale and "what to write" go in the analysis `.md` (step 7), not in the sheet.

If Ahrefs is unavailable or this step fails (auth/permission/no rows): skip the gap analysis, still
produce the workbook, put the reason in the "Content gap" sheet header and the analysis `.md`, and do not
fail the run. (If step 4 already established Ahrefs is unavailable, skip this step for the same reason.)

### 6. Write the Excel workbook (static artifact #1)

Read the bundled `xlsx` skill (`SKILL.md` for the `xlsx` skill in the available skills list) for how
to build the file, then write `seo-article-audit-<slug>.xlsx` to the outputs folder with three sheets:

- **"GSC queries"**: a small page-summary block at the top (clicks/impressions current, previous,
  Δ abs, Δ %), then the full query table with the columns from step 3. Sort by click loss
  (most negative Δ clicks first), matching the GSC report order.
- **"Ahrefs keywords"** (the second tab): columns `Keyword`, `Language`, `Country`, `Volume`,
  `Best position (current)`, `Best position (comparison)`, `Position change`. Use `keyword` first,
  then `keyword_prev` when `keyword` is null. Render a null current position as a dash. Sort by
  volume desc (dropped keywords — null current position — kept). If Ahrefs was skipped, leave a one-line note in row 1
  explaining why and emit the sheet with headers only.
- **"Content gap"** (the third tab), from step 5. Two stacked tables: (1) a competitor block — one row
  per selected competitor URL with columns `Competitor URL`, `Keywords in common`, `Keywords competitor
  only`, `Share`, `Domain rating`, `Traffic`; (2) a gap-keyword block — columns `Keyword`, `Volume`,
  `Ranking competitor(s) (pos ≤10)`, sorted by volume desc. Data only — no editorial commentary in the
  sheet. If step 5 was skipped, leave a one-line note in row 1 explaining why and emit the sheet with
  headers only.

### 7. Write the analysis Markdown (static artifact #2)

Write `seo-article-audit-<slug>-analysis.md` — the voiceover / editorial synthesis over all three sheets. Cover:
which periods/dates were used, the headline click/impression movement, the biggest query-level
losses and likely cause (position drop vs CTR vs impressions — compute CTR yourself where needed),
how the Ahrefs keyword/position picture lines up with the GSC losses (lost or worsened terms), and what
the content gap shows — **including which competitors you selected and why (the intent rationale), and
which high-overlap candidates you deliberately excluded as intent-mismatched** — then which high-volume
gap keywords are the clearest opportunities. State only what the data supports; if Ahrefs or the gap step
was skipped, say so and scope the analysis accordingly.

### 8. Present the files

Call `present_files` with both paths: the `.xlsx` and the `-analysis.md`. These are the static
artifacts. Do NOT call `show_widget`, `create_artifact`, or `update_artifact`.

### 9. Done

Tell the user how many GSC queries and Ahrefs keywords were found, which competitors you selected (and
why), how many gap keywords surfaced, which periods/dates were used, and (if Ahrefs or the gap step was
skipped) why.

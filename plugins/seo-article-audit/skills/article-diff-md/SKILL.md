---
name: article-diff-md
description: >
  Format an article (e.g. an AIHR.com blog post) into a single markdown file
  where the whole article body sits inside one ```diff code block, with pre-marked
  changes shown as red (removed, `-`) and green (added, `+`) lines. The file gets a
  title, a short voice-over intro explaining the changes, then the full wrapped diff
  block. TRIGGERS: "turn this article into a diff block", "diff-block markdown",
  "article diff md", "export article as a git diff", "show the changes as red/green
  in one code block", "/article-diff-md".
  This skill is purely the DELIVERY / FORMATTING mechanism. It does NOT decide what
  edits to make — the caller (or a separate skill) supplies the article text with the
  changes already marked. This skill only fetches/cleans the article, wraps it in one
  diff block, hard-wraps lines, writes the intro, and outputs the .md file.
---

# Article → single diff-block markdown

Take an article plus its pre-marked changes and produce one markdown file in which
the entire article body lives inside a single fenced ` ```diff ` code block. Lines
beginning with `-` render red (removed) and lines beginning with `+` render green
(added) on GitHub/GitLab; all other lines are space-prefixed context.

This skill is the formatter only. It assumes the changes have already been decided
and marked. It does not invent or choose edits.

## Input contract

The caller provides **both**:

1. **A source** — either an article URL (typically `aihr.com/blog/...`) **or** the
   article text pasted directly.
2. **Pre-marked text** — the article (or just the changed portions) with the edits
   already expressed as diff lines: each removed line prefixed `-`, each added line
   prefixed `+`. Unchanged paragraphs need no prefix; this skill adds the leading
   space.

If only a URL is given with the marked changes described separately, fetch the URL
(see Step 1), then splice the supplied `-`/`+` lines into the matching spots in the
extracted text.

## Workflow

### Step 1 — Get the article text

- If given a URL, fetch it with the web fetch tool. AIHR pages return a large
  HTML-to-text dump. The fetched result may be saved to a temp file if large.
- Extract **only the meat of the article**: the `# Title`, the author/byline and
  read-time line if present, the intro paragraphs, every `## N. <trend/section>`
  heading with its body paragraphs and "The bottom line" sentences, and the closing
  section (e.g. "Over to you"). 
- **Strip** all boilerplate: site nav, cookie/GTM scripts, social-share links,
  newsletter/CTA banners, "PREVIEW LESSONS" promo boxes, image markup, author bios
  at the very bottom, and tracking query strings on links. Keep inline factual stats
  but you may drop bare hyperlink URLs, keeping the linked phrase as plain text.
- If given pasted text instead, use it as-is as the article body.

### Step 2 — Apply / confirm the marked changes

- The changes come in already marked. Each change is a removed line (`-`) immediately
  followed by its replacement added line (`+`), or a pure addition (`+` only) / pure
  removal (`-` only).
- Do not create, alter, or remove changes. If the caller described changes against a
  URL you fetched, locate the matching sentence in the extracted text and replace it
  with the supplied `-` old / `+` new pair.

### Step 3 — Assemble the document

Structure, in this order:

1. **Title** — a top-level `# ` heading naming the file's purpose, e.g.
   `# HR Trends 2026 — single diff code block`.
2. **Intro voice-over** — a short prose paragraph (no bullets) that walks the reader
   through each change in plain language: what was changed and where (which title /
   which section), framed as "First… Second… Third…". End by noting each change shows
   as a red line (old) directly above a green line (new). Do **not** include meta
   instructions about how diff coloring works unless the caller asks — keep it to the
   walkthrough of the actual changes.
3. **The diff block** — open with a line containing only ` ```diff `, then the entire
   article body, then a closing ` ``` ` fence. Optionally start the block with a
   `@@ ... @@` hunk header for flavor.

### Step 4 — Wrap lines inside the diff block

Diff code blocks do **not** reflow, so long paragraphs render as very wide single
lines. Hard-wrap every line **inside** the block to ~80 characters, preserving the
leading prefix (`-`, `+`, or space) on every wrapped fragment so the coloring stays
intact. Use the helper:

```
python3 scripts/wrap_diff.py <input.md> [--width 80]
```

It rewrites the file in place, wrapping only content between the ` ```diff ` and
closing ` ``` ` fences, repeating the line's prefix on each wrapped line. `@@` hunk
headers and blank lines are left untouched. Default width is 80.

### Step 5 — Output

- Write the final file to the user's selected folder (vault root) as
  `<article-slug>-diff.md` (e.g. `hr-trends-2026-diff.md`).
- Present the file to the user.
- Add a one-line source citation at the bottom linking the original article URL when
  one was provided.

## Notes

- Red/green coloring only renders on GitHub, GitLab, and similar renderers. The
  Obsidian default preview and many in-app previews show the raw `-`/`+` text. Mention
  this to the user once after delivering.
- A leading space after the `-`/`+` prefix (e.g. `+ text`) is fine — GitHub still
  colors any line whose first character is `+` or `-`.

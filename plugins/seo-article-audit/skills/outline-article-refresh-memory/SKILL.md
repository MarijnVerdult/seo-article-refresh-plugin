---
name: outline-article-refresh-memory
description: >-
  Create and maintain monthly Outline memory records for AIHR SEO article refresh work,
  as part of the seo-article-audit plugin. Use ONLY within an active SEO article refresh:
  gathering GSC/Ahrefs SEO data for a specific article, running or reviewing an article
  audit, suggesting article refresh changes, preparing final article edits, attaching
  GSC/Ahrefs/Excel/CSV refresh artifacts, or checking whether analysis or changes were
  already done for an article. Within that context the assistant owns keeping the AIHR
  SEO Article Refresh Outline collection current without being asked. Do NOT use this
  skill for general file/folder work, note-taking, documentation, memory, or storage that
  is not part of an SEO article refresh — it does not govern where unrelated content is
  saved. For anything outside SEO article refresh, ignore this skill and use the default
  storage location (the user's selected workspace folder), not Outline.
---
# Outline article refresh memory

Use Outline as the persistent, user- and session-agnostic memory for AIHR SEO article
refresh work. The target collection is **AIHR-seo-article-refresh** in the AIHR Outline
workspace.

## Scope — when this skill applies

This skill applies **only** inside an active AIHR SEO article refresh, i.e. work driven by
the `seo-article-audit` plugin: auditing a specific article, pulling GSC/Ahrefs data for
it, proposing or producing refresh edits, or recording those results. The Outline
collection is a dedicated SEO-refresh memory, not a general store.

## When NOT to use this skill

Do not invoke this skill, and do not write to Outline, when the work is not an SEO article
refresh. In particular:

- General requests to inspect, list, organize, or summarize files and folders in the
  workspace.
- Note-taking, documentation, "remember this", or "save this" requests unrelated to an
  SEO article refresh.
- Any task where the user has not asked for SEO/article-refresh work and no audit is in
  progress.

In all of these cases, ignore this skill and fall back to the **default storage
location** — the user's selected workspace folder. Do not create Outline records, do not
search the SEO-refresh collection, and do not treat Outline as the default memory. Only
the SEO article refresh workflow described below uses Outline.

## Proactive responsibility

Once an SEO article refresh is underway, the assistant is responsible for keeping Outline
current. Trigger this skill when actively doing SEO article refresh work, even if the user
does not mention Outline. This proactivity is scoped to SEO article refresh only — it is
not a reason to use Outline for any other task (see "When NOT to use this skill" above).

Use this skill before and after related work:

- **Before gathering data or suggesting changes:** search Outline for the article slug
  and URL, then use prior records to avoid repeating analysis, repeated edits, or
  previously reverted ideas.
- **After gathering data:** create or update the current monthly record with exact
  summary data and links to source artifacts.
- **After recommending changes:** add the executive summary, refresh strategy, and
  proposed optimizations.
- **After final edits are produced or approved:** add the full article changes as a
  single `diff` block and link implementation artifacts.
- **After adding a new monthly record:** update the collection overview/table of
  contents with the new document link.

Do not make the user remember this workflow. If an SEO audit, article refresh, content
gap analysis, GSC/Ahrefs pull, or final article diff creates reusable knowledge, capture
it in Outline.

## Core rules

- Create **one document per article per month**.
- Title format: `YYYY-MM-article-slug`, for example `2026-06-performance-management`.
- Before running a fresh analysis or proposing edits, search Outline for the slug and
  URL. Check the current month first, then older monthly records.
- Do not append a future month into an old record. Create a new monthly record and link older records from it.
- Store supporting files in the monthly record under `Source files`.
- Store actual article edits in `Full article changes` as one `diff` block, matching the `article-diff-md` skill style.
- Keep the collection overview useful as the table of contents. Add a link whenever a new monthly record is created.

## Outline workflow

1. Find the collection with `list_collections(query="AIHR-seo-article-refresh")`.
2. Search for existing records with `list_documents(collectionId=..., query=<slug>)` and, if useful, also search by full URL.
3. If the current month record already exists, update it instead of creating a duplicate,
   unless the user explicitly asks for a second record. If a duplicate is needed, use a
   clear suffix such as `YYYY-MM-slug-analysis-2`.
4. Get the monthly record template with `list_templates(collectionId=...)`. Use the template titled `Monthly Article Refresh Record - Template`.
5. Create the monthly document from that template with `create_document(collectionId=..., templateId=..., title=...)`. Do not pass an `icon` or `color` value.
6. Upload or link supporting files, then add them to `Source files`.
7. Update the collection overview/table of contents with a bullet linking the new record.

## Monthly document template

Do not keep or recreate the monthly record template in this skill. The source of truth is
the template stored in the AIHR Outline workspace. When creating a new monthly record, retrieve the existing Outline template with `list_templates(collectionId=...)`, create the record with its `templateId`, and fill what is known; leave unknown fields blank.

Outline document markdown must not start with an H1.

## Executive summary guidance

The executive summary is not a generic status note. It must explain:

- what the data says happened;
- what traffic, query group, or position the refresh is trying to win back or improve;
- the refresh strategy;
- the concrete optimizations being made.

Example:

```text
The data shows that we lost traffic on the primary keyword. Search intent has not
meaningfully changed, and the page still matches what users are looking for.

Our refresh strategy is to double down and try to win back position on the primary
keyword.

We are making these optimizations:
1. Rewrite the intro so it answers the primary query faster.
2. Expand the section that competitors cover more deeply.
3. Update the examples and internal links so the page feels fresher and more complete.

Status: Proposed
```

## Supporting files and attachments

Outline supports attachments through `create_attachment`, which returns a private upload URL, form fields, and an Outline attachment redirect URL.

For local workspace files, get explicit user approval before uploading organization data
to Outline. Once approved:

1. Get file size and MIME type locally.
2. Call `create_attachment(name=..., contentType=..., size=...)`.
3. Upload the bytes to the returned `uploadUrl` with the returned multipart form fields
   and `file=@<local_path>`.
4. Use the returned `attachment.url` in the monthly record's `Source files` field.

If the file is already in another system such as Google Drive, GitHub, WordPress, or a CMS revision history, link that source instead of re-uploading unless the user asks for an
Outline attachment.

## Approval handling for Outline writes

Creating or updating the monthly Outline document is part of the SEO refresh workflow. If a tool call to create or update an Outline record is blocked, rejected, or requires explicit approval, stop immediately and ask the user:

```text
Do I have your approval to save this SEO audit record to the AIHR-seo-article-refresh Outline collection?
```

Do not continue to a final answer while leaving the memory update unresolved. Do not silently skip the update. If the user approves, retry the Outline write and then return the Outline document link. If the user declines or withholds approval, state that the audit memory update is not complete because approval was not granted.

## Updating the collection overview

After creating a monthly record, update the collection overview so it stays the table of
contents. Add a bullet in the existing `Table of contents` section:

```markdown
- [YYYY-MM-slug](https://aihr.getoutline.com/doc/...) - Month YYYY record for the article, with uploaded source files if applicable.
```

## Safety and quality checks

- Do not state inferences as facts. Label interpretation clearly.
- Do not create duplicate monthly records by accident.
- Do not upload local files to Outline without explicit user approval.
- Do not treat a blocked or approval-required Outline write as optional. Ask for approval immediately and retry after approval.
- Do not overwrite a human-edited collection overview with a shorter generated one.
- After creating a record, return the Outline document link and any attachment links.

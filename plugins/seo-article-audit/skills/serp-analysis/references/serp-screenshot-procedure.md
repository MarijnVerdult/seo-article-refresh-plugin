# SERP Screenshot Procedure

Use this procedure when the SEO Article Audit plugin needs a visual capture of a Google SERP for a keyword using the fixed US geolocation setup.

## Goal

Capture a full-page screenshot of a Google results page for a keyword, with the AI Overview expanded when present, using a US-localized Google URL.

## URL Template

Always build the SERP URL from `https://www.google.com/search`.

**Gotcha:** use the full UULE value below on every SERP — primary keyword, secondary keyword, or standalone capture. Never omit or shorten UULE because the keyword is secondary or because you already captured another SERP in the same audit.

Required query parameters:

```text
q={URL_ENCODED_KEYWORD}
hl=en
gl=US
ie=utf-8
oe=utf-8
pws=0
uule=a+cm9sZToxCnByb2R1Y2VyOjEyCnByb3ZlbmFuY2U6Ngp0aW1lc3RhbXA6MTc4MjE5Njk0NjgzMTAwMApsYXRsbmd7CmxhdGl0dWRlX2U3OjM3NDIxMDAwMApsb25naXR1ZGVfZTc6LTEyMjA4NDAwMDAKfQpyYWRpdXM6OTMwMDA%3D
```

Example:

```text
https://www.google.com/search?q=keyword&hl=en&gl=US&ie=utf-8&oe=utf-8&pws=0&uule=a+cm9sZToxCnByb2R1Y2VyOjEyCnByb3ZlbmFuY2U6Ngp0aW1lc3RhbXA6MTc4MjE5Njk0NjgzMTAwMApsYXRsbmd7CmxhdGl0dWRlX2U3OjM3NDIxMDAwMApsb25naXR1ZGVfZTc6LTEyMjA4NDAwMDAKfQpyYWRpdXM6OTMwMDA%3D
```

Do not reuse a `sei` value from a previous SERP URL. Google can generate or alter session-specific parameters after navigation.

## Browser Requirements

Use the user's real browser profile. Do not use standalone Playwright, bundled/headless Chromium, or an in-app browser for Google SERP capture unless the user explicitly approves that fallback after the user-browser path fails.

### Codex

Use Chrome through the Codex Chrome plugin / Codex Chrome Extension. The extension must be installed and enabled in the exact Chrome profile that Codex controls, not just in another visible Chrome profile.

If Chrome cannot attach, first verify:

```text
1. Chrome is running.
2. The Codex Chrome Extension is installed and enabled in the selected profile.
3. The native messaging host is installed correctly.
```

If the extension is installed in the wrong profile, ask the user to open the selected Chrome profile, install or enable the extension there, then retry.

### Claude Cowork

Use the Claude Cowork browser surface or the Claude in Chrome add-on controlling the user's Chrome profile. If that connection is unavailable, stop and ask the user to enable/connect it.

### Cursor

Use **`cursor-ide-browser`** only when it controls the user's active browser context:

```text
1. browser_navigate → US-localized google.com/search URL
2. Wait for render; expand AI Overview if "Show more AI Overview" is visible
3. Scroll to top (scrollY must be 0 before capture)
4. browser_take_screenshot (full page)
5. browser_snapshot for structured module/link extraction
```

If the current environment only exposes a non-user bundled browser, stop and ask for the appropriate browser connection. Do not proceed with bundled/headless browser capture.

## Capture Sequence

Follow this order exactly. It avoids the issue where the first organic result renders incorrectly in a full-page screenshot after expanding the AI Overview.

```text
1. Open a fresh Chrome tab.
2. Navigate to the generated google.com/search URL.
3. Wait for the SERP to finish initial rendering.
4. Confirm the first result and AI Overview are present in the page text when applicable.
5. If a "Show more AI Overview" button exists, click it.
6. Wait briefly for the expanded AI Overview layout to settle.
7. Scroll back to the top of the page.
8. Verify the page scroll position is 0.
9. Take the full-page screenshot.
10. Save the screenshot with a keyword-specific filename.
```

## Chrome Automation Notes

In the Chrome plugin, the practical sequence is:

```js
const url = buildGoogleSerpUrl(keyword);
const tab = await browser.tabs.new();
await tab.goto(url);
await tab.playwright.waitForLoadState({ state: "domcontentloaded", timeoutMs: 15000 });
await tab.playwright.waitForTimeout(5000);

const showMore = tab.playwright.getByRole("button", { name: "Show more AI Overview" });
if (await showMore.count() === 1) {
  await showMore.click({});
  await tab.playwright.waitForTimeout(2500);
}

await tab.playwright.evaluate(() => {
  window.scrollTo({ top: 0, left: 0, behavior: "instant" });
}, undefined, { timeoutMs: 10000 });

const state = await tab.playwright.evaluate(() => ({
  scrollY: window.scrollY,
  scrollHeight: document.documentElement.scrollHeight,
  aiOverviewExpanded: ![...document.querySelectorAll('[role="button"],button,div,span')]
    .some((el) =>
      (el.getAttribute("aria-label") || el.textContent || "")
        .trim()
        .includes("Show more AI Overview") &&
      !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length)
    ),
}), undefined, { timeoutMs: 10000 });

if (state.scrollY !== 0) {
  throw new Error("SERP screenshot aborted: page is not scrolled to the top.");
}

const pngBytes = await tab.screenshot({ fullPage: true });
```

Do not set `document.documentElement.scrollTop` or `document.body.scrollTop` in the read-only browser context. Use `window.scrollTo(...)` instead.

## Filename Convention

Use a deterministic filename based on the keyword:

```text
serp-{slugified-keyword}-us-ai-overview.png
```

Example:

```text
serp-keyword-us-ai-overview.png
```

## Verification Checklist

Before considering the screenshot valid, confirm:

```text
1. The current URL starts with https://www.google.com/search.
2. The URL contains hl=en, gl=US, pws=0, and the fixed UULE value.
3. The page text includes the first visible organic result.
4. If AI Overview is present, "Show more AI Overview" is no longer visible after expansion.
5. window.scrollY is 0 immediately before screenshot capture.
6. The screenshot is full-page, not viewport-only.
```

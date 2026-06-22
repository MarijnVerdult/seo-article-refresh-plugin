#!/usr/bin/env python3
"""Hard-wrap lines inside a ```diff code block to a target width.

Only content between an opening ```diff fence and its closing ``` fence is
wrapped. Each wrapped fragment keeps the original line's diff prefix ('-', '+',
or a single space for context) so GitHub/GitLab diff coloring stays intact.
Blank lines and `@@ ... @@` hunk headers are left untouched.

Usage:
    python3 wrap_diff.py <file.md> [--width 80]

Rewrites <file.md> in place.
"""
import argparse
import sys
import textwrap


def wrap_diff(text: str, width: int) -> str:
    lines = text.split("\n")
    out = []
    in_diff = False
    # content wrap target leaves room for the 1-char prefix + 1 space
    content_width = max(20, width - 2)

    for line in lines:
        stripped = line.strip()
        if not in_diff:
            out.append(line)
            if stripped == "```diff":
                in_diff = True
            continue

        # inside the diff block
        if stripped == "```":
            in_diff = False
            out.append(line)
            continue

        if line == "":
            out.append(line)
            continue

        prefix = line[0]
        # leave hunk headers and any non diff-prefix line as-is
        if prefix not in (" ", "-", "+"):
            out.append(line)
            continue

        content = line[1:].lstrip(" ")
        if content == "":
            out.append(prefix)
            continue

        wrapped = textwrap.wrap(
            content,
            width=content_width,
            break_long_words=False,
            break_on_hyphens=False,
        )
        for w in wrapped:
            out.append(f"{prefix} {w}")

    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description="Wrap lines inside a ```diff block.")
    ap.add_argument("file", help="Markdown file to rewrite in place")
    ap.add_argument("--width", type=int, default=80, help="Target line width (default 80)")
    args = ap.parse_args()

    with open(args.file, encoding="utf-8") as fh:
        original = fh.read()

    result = wrap_diff(original, args.width)

    with open(args.file, "w", encoding="utf-8") as fh:
        fh.write(result)

    print(f"Wrapped diff block in {args.file} to ~{args.width} chars.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

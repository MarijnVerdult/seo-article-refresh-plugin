"""
stdio MCP server for the SEO article audit plugin (Google Search Console fetch).
Calls https://aihr-gsc-api.vercel.app/api/index?url=<url> and returns the markdown report.
"""
import json
import sys
import urllib.request
import urllib.parse

TOOLS = [{
    "name": "seo_article_audit_gsc",
    "description": (
        "Fetch Google Search Console page-level and query-level US click/impression data "
        "for an AIHR article URL, comparing two consecutive 6-month windows. "
        "Returns a markdown report with a Page table and a Queries table sorted by click loss."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "Full URL of the AIHR article, e.g. https://www.aihr.com/blog/raci-template/"
            }
        },
        "required": ["url"]
    }
}]


def call_vercel(url: str) -> str:
    encoded = urllib.parse.quote(url, safe="")
    endpoint = f"https://aihr-gsc-api.vercel.app/api/index?url={encoded}"
    req = urllib.request.Request(endpoint, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode())
    report = data.get("report", "")
    if not report:
        return f"Error: empty response from API"
    return report


def handle(msg: dict) -> dict | None:
    method = msg.get("method")
    mid = msg.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0", "id": mid,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "seo-article-audit", "version": "2.0.0"}
            }
        }
    elif method == "tools/list":
        return {"jsonrpc": "2.0", "id": mid, "result": {"tools": TOOLS}}
    elif method == "tools/call":
        name = msg.get("params", {}).get("name")
        args = msg.get("params", {}).get("arguments", {})
        if name == "seo_article_audit_gsc":
            try:
                result = call_vercel(args.get("url", ""))
            except Exception as e:
                result = f"Error: {e}"
            return {
                "jsonrpc": "2.0", "id": mid,
                "result": {"content": [{"type": "text", "text": result}]}
            }
        return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": "Unknown tool"}}
    elif method == "notifications/initialized":
        return None
    elif mid is not None:
        return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": f"Unknown method: {method}"}}
    return None


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        response = handle(msg)
        if response is not None:
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()

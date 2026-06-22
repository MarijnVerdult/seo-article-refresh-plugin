"""
stdio MCP server for the SEO article audit plugin (Google Search Console fetch).
Calls the AIHR GSC API with Google ID-token bearer auth and returns the markdown report.
"""
import base64
import hashlib
import json
import os
import secrets
import sys
import time
import urllib.request
import urllib.parse
import urllib.error
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

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

DEFAULT_API_BASE = "https://aihr-gsc-api.vercel.app"
TOKEN_SKEW_SECONDS = 60


def api_base() -> str:
    return os.environ.get("AIHR_GSC_API_BASE", DEFAULT_API_BASE).rstrip("/")


def cache_path() -> Path:
    root = os.environ.get("XDG_CACHE_HOME")
    if root:
        base = Path(root)
    else:
        base = Path.home() / ".cache"
    return base / "seo-article-audit" / "google-auth.json"


def read_cache() -> dict:
    path = cache_path()
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def write_cache(data: dict) -> None:
    path = cache_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))
    try:
        path.chmod(0o600)
    except OSError:
        pass


def decode_jwt_payload(token: str) -> dict:
    try:
        payload = token.split(".")[1]
        payload += "=" * (-len(payload) % 4)
        return json.loads(base64.urlsafe_b64decode(payload.encode()))
    except Exception:
        return {}


def cached_id_token() -> str | None:
    data = read_cache()
    token = data.get("id_token")
    if not token:
        return None
    exp = int(data.get("expires_at") or decode_jwt_payload(token).get("exp") or 0)
    if exp - TOKEN_SKEW_SECONDS <= int(time.time()):
        return None
    return token


def fetch_auth_config() -> dict:
    endpoint = f"{api_base()}/api/auth-config"
    req = urllib.request.Request(endpoint, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        try:
            data = json.loads(e.read().decode())
            detail = data.get("error") or e.reason
        except Exception:
            detail = e.reason
        raise RuntimeError(f"Could not load auth config: {detail}") from e
    if data.get("error"):
        raise RuntimeError(data["error"])
    if not data.get("google_client_id"):
        raise RuntimeError("Auth config did not include google_client_id")
    return data


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def run_local_oauth(config: dict) -> str:
    client_id = config["google_client_id"]
    hosted_domain = config.get("hosted_domain") or "aihr.com"
    state = secrets.token_urlsafe(32)
    verifier = secrets.token_urlsafe(64)
    challenge = b64url(hashlib.sha256(verifier.encode()).digest())
    result: dict[str, str] = {}

    class CallbackHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            if parsed.path != "/callback":
                self.send_error(404)
                return
            if (params.get("state") or [""])[0] != state:
                self.send_error(400, "Invalid state")
                return
            if params.get("error"):
                result["error"] = (params.get("error_description") or params.get("error") or ["OAuth failed"])[0]
            else:
                result["code"] = (params.get("code") or [""])[0]

            body = b"AIHR SEO Article Audit is authenticated. You can close this tab."
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass

    server = HTTPServer(("127.0.0.1", 0), CallbackHandler)
    server.timeout = 300
    redirect_uri = f"http://127.0.0.1:{server.server_port}/callback"
    auth_params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
        "hd": hosted_domain,
        "prompt": "select_account",
    }
    auth_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(auth_params)

    print(f"Opening Google login for {hosted_domain} access...", file=sys.stderr)
    if not webbrowser.open(auth_url):
        print(f"Open this URL to authenticate: {auth_url}", file=sys.stderr)
    server.handle_request()
    server.server_close()

    if result.get("error"):
        raise RuntimeError(result["error"])
    code = result.get("code")
    if not code:
        raise RuntimeError("Google login did not return an authorization code")

    token_body = urllib.parse.urlencode({
        "client_id": client_id,
        "code": code,
        "code_verifier": verifier,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri,
    }).encode()
    req = urllib.request.Request(
        "https://oauth2.googleapis.com/token",
        data=token_body,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        token_data = json.loads(resp.read().decode())
    token = token_data.get("id_token")
    if not token:
        raise RuntimeError("Google token response did not include an ID token")

    payload = decode_jwt_payload(token)
    write_cache({
        "id_token": token,
        "expires_at": int(payload.get("exp") or (time.time() + int(token_data.get("expires_in") or 3600))),
        "email": payload.get("email"),
        "hd": payload.get("hd"),
    })
    return token


def get_id_token() -> str:
    token = cached_id_token()
    if token:
        return token
    return run_local_oauth(fetch_auth_config())


def call_vercel(url: str) -> str:
    encoded = urllib.parse.quote(url, safe="")
    endpoint = f"{api_base()}/api/gsc-lookup?url={encoded}"
    req = urllib.request.Request(endpoint, headers={
        "Accept": "application/json",
        "Authorization": f"Bearer {get_id_token()}",
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        try:
            data = json.loads(e.read().decode())
            detail = data.get("error") or e.reason
        except Exception:
            detail = e.reason
        return f"Error: {detail}"
    if data.get("error"):
        return f"Error: {data['error']}"
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

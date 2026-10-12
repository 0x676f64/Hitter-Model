#!/usr/bin/env python3
"""Local helper for the Postseason Hitter Model.

Serves hitter-model.html at http://localhost:8765 and relays data requests to
MLB's public endpoints (statsapi.mlb.com, baseballsavant.mlb.com). Browsers
block a page from reading Savant directly; this relay runs on your machine,
so the page can pull Savant leaderboards live.

Python 3.8+ standard library only. Usage:
    python3 serve.py            # opens your browser
    python3 serve.py --port 9000 --no-browser
"""
import argparse
import http.server
import socketserver
import threading
import time
import urllib.parse
import urllib.request
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PAGE = ROOT / "hitter-model.html"
ALLOWED_HOSTS = {"statsapi.mlb.com", "baseballsavant.mlb.com"}
CACHE_SECONDS = 600
UA = "Mozilla/5.0 (Postseason Hitter Model local helper)"

_cache = {}
_lock = threading.Lock()


def fetch(url):
    now = time.time()
    with _lock:
        hit = _cache.get(url)
        if hit and now - hit[0] < CACHE_SECONDS:
            return hit[1], hit[2]
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=45) as r:
        body = r.read()
        ctype = r.headers.get("Content-Type", "application/octet-stream")
    with _lock:
        _cache[url] = (now, body, ctype)
    return body, ctype


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print("  " + (fmt % args))

    def send(self, code, body, ctype="text/plain; charset=utf-8"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        if path in ("/", "/index.html", "/hitter-model.html"):
            if not PAGE.exists():
                return self.send(404, b"hitter-model.html not found next to serve.py")
            return self.send(200, PAGE.read_bytes(), "text/html; charset=utf-8")
        if path == "/proxy/ping":
            return self.send(200, b"ok")
        if path == "/proxy":
            target = urllib.parse.parse_qs(parsed.query).get("u", [""])[0]
            host = urllib.parse.urlparse(target).hostname or ""
            if not target.startswith("https://") or host not in ALLOWED_HOSTS:
                return self.send(400, b"Only statsapi.mlb.com and baseballsavant.mlb.com are relayed.")
            try:
                body, ctype = fetch(target)
                return self.send(200, body, ctype)
            except Exception as e:  # network error, HTTP error, timeout
                return self.send(502, f"Upstream request failed: {e}".encode())
        return self.send(404, b"Not found")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--no-browser", action="store_true")
    args = ap.parse_args()
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    with http.server.ThreadingHTTPServer(("127.0.0.1", args.port), Handler) as srv:
        url = f"http://localhost:{args.port}/"
        print(f"Postseason Hitter Model running at {url}  (Ctrl+C to stop)")
        if not args.no_browser:
            threading.Timer(0.6, lambda: webbrowser.open(url)).start()
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")


if __name__ == "__main__":
    main()

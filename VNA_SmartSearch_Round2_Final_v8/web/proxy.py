#!/usr/bin/env python3
"""
Local proxy for the AI version of the demo (index-ai.html).

Why this exists:
  The browser must NEVER hold your Anthropic API key. This tiny proxy sits
  between the web app and the Anthropic API, injecting the key server-side.

Run:
  export ANTHROPIC_API_KEY=sk-ant-...        # your key
  python proxy.py                            # serves on http://localhost:8787

Then open the AI web app (see README). No extra libraries needed — standard
library only.
"""
import json
import os
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = 8787
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
MAX_BODY_BYTES = 1_000_000


class Handler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        if self.path != "/health":
            self._json(404, {"error": {"message": "Not found"}})
            return
        self._json(200, {
            "status": "ok",
            "provider": "anthropic",
            "api_key_configured": bool(API_KEY),
        })

    def do_POST(self):
        if self.path != "/api/agent":
            self.send_response(404)
            self._cors()
            self.end_headers()
            return
        if not API_KEY:
            self._json(500, {"error": {"message":
                "ANTHROPIC_API_KEY not set. Run: export ANTHROPIC_API_KEY=sk-ant-..."}})
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            if length <= 0 or length > MAX_BODY_BYTES:
                self._json(413, {"error": {"message": "Invalid request size"}})
                return
            body = self.rfile.read(length)
            req = urllib.request.Request(
                ANTHROPIC_URL, data=body, method="POST",
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": API_KEY,
                    "anthropic-version": "2023-06-01",
                },
            )
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = resp.read()
            self._json_raw(200, data)
        except urllib.error.HTTPError as e:
            self._json_raw(e.code, e.read())
        except Exception as e:
            self._json(500, {"error": {"message": str(e)}})

    def _json(self, code, obj):
        self._json_raw(code, json.dumps(obj).encode())

    def _json_raw(self, code, raw_bytes):
        self.send_response(code)
        self._cors()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(raw_bytes)

    def log_message(self, *args):
        pass  # quiet


if __name__ == "__main__":
    key_state = "SET" if API_KEY else "NOT SET — export ANTHROPIC_API_KEY first"
    print(f"VNA proxy on http://localhost:{PORT}  (API key: {key_state})")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()

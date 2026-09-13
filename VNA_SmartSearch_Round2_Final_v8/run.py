#!/usr/bin/env python3
"""Reliable one-command launcher for the VNA SmartSearch demo."""

from __future__ import annotations

import argparse
import http.server
import os
import socket
import threading
import webbrowser
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
WEB_DIR = PROJECT_DIR / "web"


class ReusableThreadingHTTPServer(http.server.ThreadingHTTPServer):
    allow_reuse_address = True
    daemon_threads = True


class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
    """Prevent Safari/Chrome from showing an older demo after code updates."""

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()


def available_port(preferred: int) -> int:
    """Use the requested port when free, otherwise ask the OS for a free one."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind(("127.0.0.1", preferred))
            return preferred
        except OSError:
            sock.bind(("127.0.0.1", 0))
            return int(sock.getsockname()[1])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the VNA SmartSearch demo")
    parser.add_argument("--ai", action="store_true", help="open optional Claude-powered demo")
    parser.add_argument("--port", type=int, default=8000, help="preferred local port")
    parser.add_argument("--no-browser", action="store_true", help="do not open a browser automatically")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    page = "index-ai.html" if args.ai else "index.html"
    page_path = WEB_DIR / page
    if not page_path.is_file():
        raise SystemExit(f"Missing {page_path}. Keep run.py beside the web folder.")

    port = available_port(args.port)
    os.chdir(WEB_DIR)
    handler = NoCacheHandler
    with ReusableThreadingHTTPServer(("127.0.0.1", port), handler) as server:
        url = f"http://127.0.0.1:{port}/{page}"
        mode = "OPTIONAL AI" if args.ai else "STABLE OFFLINE"
        print(f"\nVNA SmartSearch — {mode}")
        if port != args.port:
            print(f"Port {args.port} was busy; using {port} instead.")
        if args.ai:
            print("The AI page also requires web/proxy.py and ANTHROPIC_API_KEY.")
        print(f"Open: {url}")
        print("Press Ctrl+C to stop.\n")

        if not args.no_browser:
            threading.Timer(0.5, lambda: webbrowser.open(url)).start()
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")


if __name__ == "__main__":
    main()

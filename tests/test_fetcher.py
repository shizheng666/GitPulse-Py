"""页面抓取测试。"""

from __future__ import annotations

import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from trending_monitor.fetcher import fetch_trending_page


class _SuccessHandler(BaseHTTPRequestHandler):
    """返回 200 响应的本地测试服务。"""

    def do_GET(self) -> None:  # noqa: N802
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"<html><body>ok</body></html>")

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return


class _ErrorHandler(BaseHTTPRequestHandler):
    """返回 500 响应的本地测试服务。"""

    def do_GET(self) -> None:  # noqa: N802
        self.send_response(500)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"error")

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return


def _serve(handler_cls: type[BaseHTTPRequestHandler]) -> tuple[HTTPServer, threading.Thread]:
    """启动一个本地 HTTP 服务供抓取测试使用。"""

    server = HTTPServer(("127.0.0.1", 0), handler_cls)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def test_fetch_trending_page_returns_html_text() -> None:
    """抓取成功时应返回页面 HTML 文本。"""

    server, thread = _serve(_SuccessHandler)
    url = f"http://127.0.0.1:{server.server_port}/trending"

    try:
        html = fetch_trending_page(url, timeout=5)
    finally:
        server.shutdown()
        thread.join()

    assert "ok" in html


def test_fetch_trending_page_raises_readable_error_for_http_error() -> None:
    """非 200 响应应转为中文可读错误。"""

    server, thread = _serve(_ErrorHandler)
    url = f"http://127.0.0.1:{server.server_port}/trending"

    try:
        with pytest.raises(RuntimeError, match="抓取 GitHub Trending 页面失败"):
            fetch_trending_page(url, timeout=5)
    finally:
        server.shutdown()
        thread.join()

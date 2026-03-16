"""负责抓取 GitHub Trending 页面内容。"""

from __future__ import annotations

from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/135.0.0.0 Safari/537.36"
)


def fetch_trending_page(url: str, timeout: int = 15) -> str:
    """抓取 GitHub Trending 页面 HTML。

    这里显式设置浏览器风格的 User-Agent，是为了减少被网站当成异常脚本请求的概率；
    同时统一超时和异常包装，方便主流程输出稳定、可读的中文错误信息。
    """

    request = Request(url, headers={"User-Agent": DEFAULT_USER_AGENT})

    try:
        with urlopen(request, timeout=timeout) as response:
            status_code = getattr(response, "status", response.getcode())
            if status_code != 200:
                raise RuntimeError(f"抓取 GitHub Trending 页面失败，HTTP 状态码：{status_code}")
            return response.read().decode("utf-8")
    except HTTPError as exc:
        raise RuntimeError(f"抓取 GitHub Trending 页面失败，HTTP 状态码：{exc.code}") from exc
    except URLError as exc:
        raise RuntimeError(f"抓取 GitHub Trending 页面失败，网络请求异常：{exc.reason}") from exc
    except TimeoutError as exc:
        raise RuntimeError("抓取 GitHub Trending 页面失败，请求超时") from exc

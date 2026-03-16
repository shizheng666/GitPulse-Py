"""处理 GitHub 仓库链接的工具函数。"""

from __future__ import annotations

from urllib.parse import urljoin, urlparse, urlunparse


def normalize_repo_url(base_url: str, href: str) -> str:
    """将 GitHub 页面中的仓库链接规范化为绝对 URL。"""

    if not href or not href.strip():
        raise ValueError("链接不能为空")

    # `urljoin` 可以把 `/owner/repo` 这样的相对路径自动补全成完整地址。
    absolute_url = urljoin(base_url, href.strip())
    parsed = urlparse(absolute_url)

    # 邮件中的仓库链接只需要稳定定位到仓库主页，因此主动去掉 fragment。
    normalized = urlunparse(
        (parsed.scheme, parsed.netloc, parsed.path, parsed.params, parsed.query, "")
    )

    return normalized

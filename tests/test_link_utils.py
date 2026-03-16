"""链接处理模块测试。"""

from __future__ import annotations

import pytest

from trending_monitor.link_utils import normalize_repo_url


def test_normalize_repo_url_converts_relative_path_to_absolute_url() -> None:
    """相对路径应该能被补全为 GitHub 绝对地址。"""

    result = normalize_repo_url("https://github.com/trending", "/owner/repo")

    assert result == "https://github.com/owner/repo"


def test_normalize_repo_url_removes_fragment() -> None:
    """带锚点的链接应该移除 fragment，避免通知中出现脏链接。"""

    result = normalize_repo_url("https://github.com/trending", "/owner/repo#readme")

    assert result == "https://github.com/owner/repo"


def test_normalize_repo_url_raises_error_for_empty_href() -> None:
    """空链接应明确报错，交给上层决定是否跳过当前项目。"""

    with pytest.raises(ValueError, match="链接不能为空"):
        normalize_repo_url("https://github.com/trending", "")

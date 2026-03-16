"""快照保存测试。"""

from __future__ import annotations

import json

from trending_monitor.models import TrendingRepo
from trending_monitor.storage import save_snapshot


def test_save_snapshot_creates_daily_json_file(tmp_path) -> None:
    """保存快照时应自动创建目录并写出 JSON 文件。"""

    items = [
        TrendingRepo(
            repo_name="openai/openai-python",
            repo_url="https://github.com/openai/openai-python",
            description="OpenAI Python SDK",
            language="Python",
            stars=12345,
            forks=1234,
            stars_today=567,
            fetched_at="2026-03-16T09:00:00+08:00",
        )
    ]

    output_path = save_snapshot(items, str(tmp_path / "data"))

    saved_file = tmp_path / "data" / "trending_2026-03-16.json"
    assert output_path == str(saved_file)
    assert saved_file.exists()

    payload = json.loads(saved_file.read_text(encoding="utf-8"))
    assert payload[0]["repo_name"] == "openai/openai-python"
    assert payload[0]["stars_today"] == 567

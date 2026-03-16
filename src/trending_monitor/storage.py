"""保存每日抓取快照。"""

from __future__ import annotations

import json
from pathlib import Path

from trending_monitor.models import TrendingRepo


def save_snapshot(items: list[TrendingRepo], data_dir: str) -> str:
    """将当天抓取结果保存为 JSON 文件。

    这里按日期命名文件，是为了让每日快照天然具备“时间切片”能力，
    后续如果要做“只提醒新上榜项目”，可以直接拿当天与前一天的快照做差异对比。
    """

    output_dir = Path(data_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    date_text = items[0].fetched_at[:10] if items else "unknown-date"
    output_path = output_dir / f"trending_{date_text}.json"

    payload = [item.to_dict() for item in items]
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return str(output_path)

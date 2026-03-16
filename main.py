"""GitHub 趋势监控脚本入口。"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse


# 允许直接运行 `python main.py` 时找到 src 目录中的项目包。
PROJECT_ROOT = Path(__file__).resolve().parent
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from trending_monitor.config import load_settings
from trending_monitor.fetcher import fetch_trending_page
from trending_monitor.notifier import build_email_html, send_email
from trending_monitor.parser import parse_trending
from trending_monitor.storage import save_snapshot


def run() -> int:
    """执行一次完整的抓取、保存与通知流程。

    整体链路如下：
    1. 读取环境配置
    2. 抓取 GitHub Trending 页面
    3. 解析热门项目
    4. 保存当天 JSON 快照
    5. 生成邮件正文并发送
    """

    try:
        # 第一步：读取运行配置，统一管理页面地址、数量限制和邮件参数。
        settings = load_settings()

        # 第二步：抓取 Trending 页面原始 HTML。
        html = fetch_trending_page(settings.trending_url, settings.fetch_timeout)

        # 第三步：把 HTML 解析成结构化仓库列表。
        parsed_base_url = f"{urlparse(settings.trending_url).scheme}://{urlparse(settings.trending_url).netloc}"
        items = parse_trending(html, parsed_base_url, settings.top_n)
        if not items:
            raise RuntimeError("解析结果为空，未找到任何热门项目，已停止发送邮件。")

        # 第四步：将当天结果保存为本地 JSON 快照，便于回溯和后续扩展。
        snapshot_path = save_snapshot(items, settings.data_dir)

        # 第五步：构造 HTML 邮件并通过 SMTP 发送。
        fetch_date = items[0].fetched_at[:10] if items else datetime.now().strftime("%Y-%m-%d")
        subject = f"GitHub 今日热门项目日报 - {fetch_date}"
        html_body = build_email_html(items, fetch_date)
        send_email(subject, html_body, settings.smtp)

        print(f"执行成功：已保存快照到 {snapshot_path}，并完成邮件发送。")
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"执行失败：{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(run())

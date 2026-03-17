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
from trending_monitor.progress import ProgressTracker
from trending_monitor.storage import save_snapshot


def create_progress_tracker() -> ProgressTracker:
    """创建一个适合当前终端环境的进度展示器。"""

    return ProgressTracker(stream=sys.stdout)


def run() -> int:
    """执行一次完整的抓取、保存与通知流程。"""

    progress = create_progress_tracker()
    current_step = "读取配置"
    progress.start(total_steps=5, initial_step=current_step)

    try:
        # 第一步：读取运行配置，统一管理页面地址、数量限制和邮件参数。
        settings = load_settings()

        # 第二步：抓取 Trending 页面原始 HTML。
        current_step = "抓取页面"
        progress.advance(current_step)
        html = fetch_trending_page(settings.trending_url, settings.fetch_timeout)

        # 第三步：把 HTML 解析成结构化仓库列表。
        current_step = "解析项目"
        progress.advance(current_step)
        parsed_url = urlparse(settings.trending_url)
        parsed_base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        items = parse_trending(html, parsed_base_url, settings.top_n)
        if not items:
            raise RuntimeError("解析结果为空，未找到任何热门项目，已停止发送邮件。")

        # 第四步：将当天结果保存为本地 JSON 快照，便于回溯和后续扩展。
        current_step = "保存快照"
        progress.advance(current_step)
        snapshot_path = save_snapshot(items, settings.data_dir)

        # 第五步：构造 HTML 邮件并通过 SMTP 发送。
        current_step = "发送邮件"
        progress.advance(current_step)
        fetch_date = items[0].fetched_at[:10] if items else datetime.now().strftime("%Y-%m-%d")
        subject = f"GitHub 今日热门项目日报 - {fetch_date}"
        html_body = build_email_html(items, fetch_date)
        send_email(subject, html_body, settings.smtp)

        message = f"执行成功：已保存快照到 {snapshot_path}，并完成邮件发送。"
        progress.finish(message)
        return 0
    except Exception as exc:  # noqa: BLE001
        progress.fail(current_step, str(exc))
        print(f"执行失败：{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(run())

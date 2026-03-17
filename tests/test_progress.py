"""终端进度展示测试。"""

from __future__ import annotations

import io

from trending_monitor.progress import ProgressTracker


class DummyStream(io.StringIO):
    """可控制是否为交互终端的测试输出流。"""

    def __init__(self, is_tty: bool) -> None:
        super().__init__()
        self._is_tty = is_tty

    def isatty(self) -> bool:
        return self._is_tty


class FakeRichProgress:
    """替代 rich.Progress 的测试桩。"""

    def __init__(self, *args, **kwargs) -> None:
        self.events: list[tuple[str, object]] = []

    def __enter__(self) -> "FakeRichProgress":
        self.events.append(("enter", None))
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.events.append(("exit", None))

    def add_task(self, description: str, total: int) -> int:
        self.events.append(("add_task", (description, total)))
        return 1

    def update(self, task_id: int, **kwargs) -> None:
        self.events.append(("update", (task_id, kwargs)))

    def stop(self) -> None:
        self.events.append(("stop", None))


def test_progress_tracker_logs_steps_in_non_interactive_mode() -> None:
    """非交互终端下应降级为普通中文日志。"""

    stream = DummyStream(is_tty=False)
    tracker = ProgressTracker(stream=stream)

    tracker.start(total_steps=5, initial_step="读取配置")
    tracker.advance("抓取页面")
    tracker.fail("抓取页面", "网络超时")

    output = stream.getvalue()
    assert "开始：读取配置" in output
    assert "已完成：读取配置" in output
    assert "开始：抓取页面" in output
    assert "失败：抓取页面 - 网络超时" in output


def test_progress_tracker_updates_rich_progress_in_interactive_mode(monkeypatch) -> None:
    """交互终端下应通过 rich 进度条更新阶段描述。"""

    stream = DummyStream(is_tty=True)
    fake_progress = FakeRichProgress()
    monkeypatch.setattr("trending_monitor.progress.Progress", lambda *args, **kwargs: fake_progress)

    tracker = ProgressTracker(stream=stream)
    tracker.start(total_steps=5, initial_step="读取配置")
    tracker.advance("抓取页面")
    tracker.finish("执行成功")

    assert ("enter", None) in fake_progress.events
    assert ("add_task", ("当前阶段：读取配置", 5)) in fake_progress.events
    assert (
        "update",
        (
            1,
            {
                "advance": 1,
                "description": "当前阶段：抓取页面",
            },
        ),
    ) in fake_progress.events
    assert (
        "update",
        (
            1,
            {
                "completed": 5,
                "description": "执行成功",
            },
        ),
    ) in fake_progress.events

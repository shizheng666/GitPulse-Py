"""终端进度展示工具。"""

from __future__ import annotations

import sys
from typing import TextIO

try:
    from rich.console import Console
    from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
except ImportError:  # pragma: no cover - 未安装 rich 时自动降级到文本日志
    Console = None
    Progress = None
    SpinnerColumn = None
    BarColumn = None
    TextColumn = None


class ProgressTracker:
    """统一管理交互式进度条和非交互日志输出。"""

    def __init__(self, stream: TextIO | None = None) -> None:
        self.stream = stream or sys.stdout
        self.is_interactive = bool(getattr(self.stream, "isatty", lambda: False)()) and Progress is not None
        self._console = Console(file=self.stream) if self.is_interactive and Console is not None else None
        self._progress = None
        self._task_id: int | None = None
        self._total_steps = 0
        self._current_step = ""

    def start(self, total_steps: int, initial_step: str) -> None:
        """开始一个新的阶段式进度展示。"""

        self._total_steps = total_steps
        self._current_step = initial_step

        if self.is_interactive:
            self._progress = Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("{task.completed}/{task.total}"),
                console=self._console,
            )
            self._progress.__enter__()
            self._task_id = self._progress.add_task(f"当前阶段：{initial_step}", total=total_steps)
            return

        print(f"开始：{initial_step}", file=self.stream, flush=True)

    def advance(self, step_name: str) -> None:
        """完成当前阶段，并切换到下一个阶段。"""

        if self.is_interactive and self._progress is not None and self._task_id is not None:
            self._progress.update(
                self._task_id,
                advance=1,
                description=f"当前阶段：{step_name}",
            )
        else:
            print(f"已完成：{self._current_step}", file=self.stream, flush=True)
            print(f"开始：{step_name}", file=self.stream, flush=True)

        self._current_step = step_name

    def fail(self, step_name: str, error: str) -> None:
        """在当前阶段失败时输出错误并关闭进度展示。"""

        message = f"失败：{step_name} - {error}"
        if self.is_interactive and self._progress is not None and self._task_id is not None:
            self._progress.update(self._task_id, description=message)
        else:
            print(message, file=self.stream, flush=True)

        self._close_progress()

    def finish(self, message: str) -> None:
        """完成全部阶段并输出最终结果。"""

        if self.is_interactive and self._progress is not None and self._task_id is not None:
            self._progress.update(
                self._task_id,
                completed=self._total_steps,
                description=message,
            )
        else:
            print(f"已完成：{self._current_step}", file=self.stream, flush=True)
            print(message, file=self.stream, flush=True)

        self._close_progress()

    def _close_progress(self) -> None:
        """安全关闭 rich 进度条上下文。"""

        if self._progress is None:
            return

        self._progress.__exit__(None, None, None)
        self._progress = None
        self._task_id = None

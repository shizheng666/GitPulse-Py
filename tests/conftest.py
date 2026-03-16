"""测试阶段的公共初始化。"""

from __future__ import annotations

import sys
from pathlib import Path


# 将 src 目录加入导入路径，便于测试直接导入项目包。
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = PROJECT_ROOT / "src"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

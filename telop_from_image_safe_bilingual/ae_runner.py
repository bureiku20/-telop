from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Optional


def find_afterfx() -> Optional[str]:
    """Attempt to locate the After Effects CLI executable."""
    return shutil.which("afterfx")


def run_after_effects(jsx_path: Path, mogrt_path: Path, afterfx_path: Optional[str] = None) -> subprocess.CompletedProcess:
    """Run After Effects with the given JSX script. Raises FileNotFoundError
    if After Effects is not installed."""
    if afterfx_path is None:
        afterfx_path = find_afterfx()
    if not afterfx_path:
        raise FileNotFoundError("After Effects executable not found")

    cmd = [afterfx_path, "-r", str(jsx_path)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if not mogrt_path.exists():
        raise RuntimeError(".mogrt export failed")
    return proc

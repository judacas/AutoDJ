"""Package initialization for ``MonolithDev.gettingSongs``."""

from __future__ import annotations

import sys
from pathlib import Path


# Ensure the package directory is available on ``sys.path`` so that modules
# imported from this package can use the existing absolute-style imports that
# rely on being able to resolve siblings such as ``logging_config``.
_PACKAGE_DIR = Path(__file__).resolve().parent
if str(_PACKAGE_DIR) not in sys.path:
    sys.path.append(str(_PACKAGE_DIR))


# Initialize configuration on module import
from config import init_config  # noqa: E402

init_config()


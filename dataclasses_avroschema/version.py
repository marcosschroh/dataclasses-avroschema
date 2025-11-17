import sys

PY_VERSION = sys.version_info


def is_python_314_or_newer() -> bool:
    return PY_VERSION >= (3, 14)

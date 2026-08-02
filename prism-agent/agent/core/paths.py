"""Central Path Resolution Utility for PyInstaller Executables and Portable Deployments."""

import os
import sys


def get_exe_dir() -> str:
    """Return absolute path to directory containing the executable or main script."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def get_bundle_dir() -> str:
    """Return PyInstaller temp extraction directory (_MEIPASS) or source root."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS  # type: ignore[attr-defined]
    return get_exe_dir()


def get_resource_path(relative_path: str) -> str:
    """
    Resolve path to a bundled or local asset file.
    Checks PyInstaller bundle (_MEIPASS), executable folder, and CWD.
    """
    # 1. Check PyInstaller _MEIPASS bundle
    bundle_path = os.path.join(get_bundle_dir(), relative_path)
    if os.path.exists(bundle_path):
        return bundle_path

    # 2. Check executable directory
    exe_path = os.path.join(get_exe_dir(), relative_path)
    if os.path.exists(exe_path):
        return exe_path

    # 3. Check CWD
    cwd_path = os.path.join(os.getcwd(), relative_path)
    if os.path.exists(cwd_path):
        return cwd_path

    # Default fallback to executable directory path
    return exe_path


def get_writable_path(filename: str) -> str:
    """
    Return writable destination path for runtime files (config, credentials, logs).
    Prefers executable directory; falls back to CWD if exe directory is non-writable.
    """
    exe_dir = get_exe_dir()
    target_path = os.path.join(exe_dir, filename)

    # Test if exe_dir is writable
    try:
        test_file = os.path.join(exe_dir, ".write_test.tmp")
        with open(test_file, "w") as f:
            f.write("test")
        os.remove(test_file)
        return target_path
    except Exception:
        # Fallback to current working directory
        return os.path.join(os.getcwd(), filename)

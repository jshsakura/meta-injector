"""Utility functions for WiiVC Injector."""
import subprocess
import urllib.request
import socket
from pathlib import Path
from typing import Optional, List


def check_internet_connection(timeout: int = 3) -> bool:
    """
    Check if internet connection is available.

    Args:
        timeout: Connection timeout in seconds

    Returns:
        True if connected, False otherwise
    """
    try:
        urllib.request.urlopen('http://clients3.google.com/generate_204', timeout=timeout)
        return True
    except (urllib.error.URLError, socket.timeout):
        return False


def run_process(
    executable: str,
    args: List[str],
    hide_window: bool = True,
    wait: bool = True,
    cwd: Optional[str] = None
) -> subprocess.CompletedProcess:
    """
    Launch external process.

    Args:
        executable: Path to executable
        args: List of arguments
        hide_window: Hide process window (Windows only)
        wait: Wait for process to complete
        cwd: Working directory

    Returns:
        CompletedProcess object with return code and output
    """
    cmd = [executable] + args

    # Hide window on Windows
    creation_flags = 0
    if hide_window and subprocess.sys.platform == 'win32':
        creation_flags = subprocess.CREATE_NO_WINDOW

    try:
        if wait:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                creationflags=creation_flags
            )
            return result
        else:
            subprocess.Popen(
                cmd,
                cwd=cwd,
                creationflags=creation_flags
            )
            return subprocess.CompletedProcess(cmd, 0)
    except Exception as e:
        print(f"Error running process: {e}")
        raise


def string_to_bytes(hex_string: str) -> bytes:
    """
    Convert hex string to bytes.

    Args:
        hex_string: Hex string like "AABBCCDD"

    Returns:
        Bytes object
    """
    return bytes.fromhex(hex_string)


def bytes_to_hex_string(data: bytes) -> str:
    """
    Convert bytes to hex string.

    Args:
        data: Bytes to convert

    Returns:
        Hex string
    """
    return data.hex().upper()


def ensure_directory(path: Path) -> Path:
    """
    Ensure directory exists, create if not.

    Args:
        path: Directory path

    Returns:
        Path object
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_short_path_name(long_path: str) -> str:
    """
    Get Windows short path name (8.3 format).

    Args:
        long_path: Long path with spaces

    Returns:
        Short path name
    """
    try:
        if subprocess.sys.platform == 'win32':
            import ctypes
            from ctypes import wintypes

            _GetShortPathNameW = ctypes.windll.kernel32.GetShortPathNameW
            _GetShortPathNameW.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD]
            _GetShortPathNameW.restype = wintypes.DWORD

            output_buf = ctypes.create_unicode_buffer(1000)
            result = _GetShortPathNameW(long_path, output_buf, 1000)

            if result:
                return output_buf.value
            else:
                return long_path
        else:
            return long_path
    except Exception:
        return long_path

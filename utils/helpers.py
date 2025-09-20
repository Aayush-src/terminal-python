"""
Utility functions for cross-platform terminal operations.
"""
import os
import platform
from pathlib import Path


def get_home_directory():
    """Get the user's home directory in a cross-platform way."""
    return str(Path.home())


def normalize_path(path, cwd):
    """
    Normalize a path relative to current working directory.

    Args:
        path (str): The path to normalize
        cwd (str): Current working directory

    Returns:
        str: Normalized absolute path
    """
    if not path:
        return cwd

    # Handle tilde expansion
    if path.startswith('~'):
        path = os.path.expanduser(path)

    # Make path absolute if it's relative
    if not os.path.isabs(path):
        path = os.path.join(cwd, path)

    # Normalize the path
    return os.path.normpath(path)


def is_safe_path(path, cwd):
    """
    Check if a path is safe to operate on (prevents dangerous operations).

    Args:
        path (str): The path to check
        cwd (str): Current working directory

    Returns:
        bool: True if path is safe, False otherwise
    """
    try:
        normalized_path = normalize_path(path, cwd)
        real_path = os.path.realpath(normalized_path)
        real_cwd = os.path.realpath(cwd)

        # Get system root directory
        system_root = os.path.abspath(os.sep)

        # Prevent operations on system root
        if real_path == system_root or real_path == system_root.rstrip(os.sep):
            return False

        # Prevent operations on critical system directories
        critical_dirs = [
            os.path.join(system_root, 'Windows', 'System32'),
            os.path.join(system_root, 'Windows', 'SysWOW64'),
            os.path.join(system_root, 'Program Files'),
            os.path.join(system_root, 'Program Files (x86)'),
            os.path.join(system_root, 'boot'),
            os.path.join(system_root, 'etc'),
            os.path.join(system_root, 'usr', 'bin'),
            os.path.join(system_root, 'usr', 'sbin'),
            os.path.join(system_root, 'bin'),
            os.path.join(system_root, 'sbin'),
        ]

        for critical_dir in critical_dirs:
            if os.path.exists(critical_dir) and real_path.startswith(critical_dir):
                return False

        # Allow operations within user's home directory
        home_dir = get_home_directory()
        real_home = os.path.realpath(home_dir)
        if real_path.startswith(real_home):
            return True

        # Allow operations within current working directory
        if real_path.startswith(real_cwd):
            return True

        # Allow operations in common user directories
        user_dirs = [
            os.path.join(system_root, 'Users'),
            os.path.join(system_root, 'home'),
            os.path.join(system_root, 'tmp'),
            os.path.join(system_root, 'temp'),
        ]

        for user_dir in user_dirs:
            if os.path.exists(user_dir) and real_path.startswith(user_dir):
                return True

        return False
    except (OSError, ValueError):
        return False


def format_file_size(size_bytes):
    """
    Format file size in human readable format.

    Args:
        size_bytes (int): Size in bytes

    Returns:
        str: Formatted size string
    """
    if size_bytes == 0:
        return "0B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1

    return f"{size_bytes:.1f}{size_names[i]}"


def get_file_permissions(file_path):
    """
    Get file permissions in a readable format.

    Args:
        file_path (str): Path to the file

    Returns:
        str: Permission string (e.g., "rwxr-xr-x")
    """
    try:
        stat_info = os.stat(file_path)
        mode = stat_info.st_mode

        # Convert to octal and get last 3 digits
        permissions = oct(mode)[-3:]

        # Convert to rwx format
        perm_map = {'0': '---', '1': '--x', '2': '-w-', '3': '-wx',
                    '4': 'r--', '5': 'r-x', '6': 'rw-', '7': 'rwx'}

        result = ''
        for digit in permissions:
            result += perm_map[digit]

        return result
    except (OSError, ValueError):
        return "---------"


def format_timestamp(timestamp):
    """
    Format timestamp in a readable format.

    Args:
        timestamp (float): Unix timestamp

    Returns:
        str: Formatted timestamp string
    """
    import datetime
    try:
        dt = datetime.datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, OSError):
        return "Unknown"


def get_platform_info():
    """
    Get platform-specific information.

    Returns:
        dict: Platform information
    """
    return {
        'system': platform.system(),
        'release': platform.release(),
        'version': platform.version(),
        'machine': platform.machine(),
        'processor': platform.processor()
    }

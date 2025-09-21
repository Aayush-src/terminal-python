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

        # Prevent operations on critical system directories (Ubuntu/Linux specific)
        critical_dirs = [
            # Core system directories
            os.path.join(system_root, 'boot'),
            os.path.join(system_root, 'etc'),
            os.path.join(system_root, 'bin'),
            os.path.join(system_root, 'sbin'),
            os.path.join(system_root, 'usr', 'bin'),
            os.path.join(system_root, 'usr', 'sbin'),
            os.path.join(system_root, 'usr', 'lib'),
            os.path.join(system_root, 'usr', 'lib64'),
            os.path.join(system_root, 'usr', 'lib32'),
            os.path.join(system_root, 'lib'),
            os.path.join(system_root, 'lib64'),
            os.path.join(system_root, 'lib32'),

            # System configuration
            os.path.join(system_root, 'var', 'log'),
            os.path.join(system_root, 'var', 'lib'),
            os.path.join(system_root, 'var', 'cache'),
            os.path.join(system_root, 'var', 'spool'),
            os.path.join(system_root, 'var', 'run'),

            # Kernel and drivers
            os.path.join(system_root, 'lib', 'modules'),
            os.path.join(system_root, 'lib', 'firmware'),

            # System services
            os.path.join(system_root, 'etc', 'systemd'),
            os.path.join(system_root, 'etc', 'init.d'),
            os.path.join(system_root, 'etc', 'rc.d'),

            # Package management
            os.path.join(system_root, 'var', 'lib', 'dpkg'),
            os.path.join(system_root, 'var', 'lib', 'apt'),
            os.path.join(system_root, 'etc', 'apt'),

            # Network configuration
            os.path.join(system_root, 'etc', 'network'),
            os.path.join(system_root, 'etc', 'netplan'),

            # Security
            os.path.join(system_root, 'etc', 'ssh'),
            os.path.join(system_root, 'etc', 'ssl'),
            os.path.join(system_root, 'etc', 'pam.d'),

            # Windows compatibility (if WSL)
            os.path.join(system_root, 'Windows', 'System32'),
            os.path.join(system_root, 'Windows', 'SysWOW64'),
            os.path.join(system_root, 'Program Files'),
            os.path.join(system_root, 'Program Files (x86)'),
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


def is_critical_system_file(file_path):
    """
    Check if a file is critical for Ubuntu system operation.

    Args:
        file_path (str): Path to the file to check

    Returns:
        bool: True if file is critical and should be protected
    """
    try:
        normalized_path = os.path.normpath(file_path)

        # Critical system files that could crash Ubuntu
        critical_files = [
            # Kernel and boot files
            '/boot/vmlinuz',
            '/boot/initrd.img',
            '/boot/grub/grub.cfg',
            '/boot/grub/grubenv',

            # Essential system binaries
            '/bin/bash',
            '/bin/sh',
            '/bin/rm',
            '/bin/mv',
            '/bin/cp',
            '/bin/ls',
            '/bin/cat',
            '/bin/mkdir',
            '/bin/rmdir',
            '/bin/chmod',
            '/bin/chown',
            '/bin/sudo',
            '/bin/su',

            # System libraries
            '/lib/ld-linux.so',
            '/lib64/ld-linux-x86-64.so',
            '/lib/systemd/systemd',

            # Configuration files
            '/etc/passwd',
            '/etc/shadow',
            '/etc/group',
            '/etc/sudoers',
            '/etc/fstab',
            '/etc/hosts',
            '/etc/resolv.conf',
            '/etc/network/interfaces',
            '/etc/systemd/system.conf',

            # Package management
            '/usr/bin/dpkg',
            '/usr/bin/apt',
            '/usr/bin/apt-get',
            '/usr/bin/apt-cache',

            # Network tools
            '/usr/bin/ssh',
            '/usr/bin/sshd',
            '/usr/sbin/sshd',

            # System services
            '/usr/bin/systemctl',
            '/usr/sbin/service',
        ]

        # Check if the file matches any critical file
        for critical_file in critical_files:
            if normalized_path == critical_file or normalized_path.endswith(critical_file):
                return True

        # Check for critical file patterns
        critical_patterns = [
            '/boot/vmlinuz-',
            '/boot/initrd.img-',
            '/lib/modules/',
            '/usr/lib/python',
            '/usr/bin/python',
            '/usr/bin/python3',
        ]

        for pattern in critical_patterns:
            if pattern in normalized_path:
                return True

        return False

    except (OSError, ValueError):
        return True  # Err on the side of caution


def is_safe_to_delete(file_path):
    """
    Check if a file is safe to delete (won't crash the system).

    Args:
        file_path (str): Path to the file to check

    Returns:
        tuple: (is_safe: bool, reason: str)
    """
    try:
        # Check if it's a critical system file
        if is_critical_system_file(file_path):
            return False, "Critical system file - deletion could crash Ubuntu"

        # Check if it's in a protected directory
        if not is_safe_path(file_path, os.getcwd()):
            return False, "File is in a protected system directory"

        # Check if it's a system binary or library
        normalized_path = os.path.normpath(file_path)
        if any(normalized_path.startswith(prefix) for prefix in ['/bin/', '/sbin/', '/usr/bin/', '/usr/sbin/', '/lib/', '/usr/lib/']):
            return False, "System binary/library - deletion could break Ubuntu"

        return True, "Safe to delete"

    except (OSError, ValueError):
        return False, "Cannot access file - assuming unsafe"


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
